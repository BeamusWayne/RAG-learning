#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Milvus MVP-04: 批量处理优化
============================
目标：学习批量处理技术，提升大规模数据摄入和查询的吞吐量
在MVP-03 RAG基础上新增：

新增内容：
- 批量插入（Batch Insert）优化
- 批量搜索（Batch Search）
- 并发批量任务（asyncio.gather）
- 进度跟踪（Progress Tracking）
- 性能指标统计

为什么要批量处理：
- 减少网络往返次数（Round Trip）
- 充分利用Milvus的批量API
- 提升整体吞吐量10-100倍

知识点：
- 批量大小（batch_size）的选择：太大导致内存压力，太小效率低
- 建议批量大小：100-1000条/批
- 并发度控制：避免过多并发连接压垮Milvus
"""

import asyncio
import numpy as np
import time
from typing import List, Dict, Optional
from dataclasses import dataclass
from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType

# ============================================================
# 第一步：性能指标数据类
# ============================================================
@dataclass
class PerformanceMetrics:
    """性能指标数据类，用于记录和报告性能数据"""
    total_items: int = 0          # 总处理条目数
    successful_items: int = 0      # 成功处理条目数
    failed_items: int = 0         # 失败条目数
    total_time: float = 0.0       # 总耗时（秒）
    items_per_second: float = 0.0 # 每秒处理条目数

    def calculate(self):
        """计算衍生指标"""
        if self.total_time > 0:
            self.items_per_second = self.successful_items / self.total_time
        return self

    def __str__(self):
        return (
            f"性能指标:\n"
            f"  总条目数: {self.total_items}\n"
            f"  成功: {self.successful_items}\n"
            f"  失败: {self.failed_items}\n"
            f"  总耗时: {self.total_time:.2f}秒\n"
            f"  吞吐量: {self.items_per_second:.2f} 条/秒"
        )

# ============================================================
# 第二步：批量处理引擎
# ============================================================
class BatchProcessor:
    """
    批量处理引擎，支持大批量数据的并发处理
    核心优化点：
    1. 批量插入：减少网络往返
    2. 批量搜索：一次查询返回多个结果
    3. 并发控制：限制同时进行的任务数
    """

    def __init__(
        self,
        collection,
        batch_size: int = 500,
        max_concurrency: int = 3
    ):
        """
        参数:
            collection: Milvus Collection对象
            batch_size: 每批处理的条目数
            max_concurrency: 最大并发任务数
        """
        self.collection = collection
        self.batch_size = batch_size
        self.max_concurrency = max_concurrency
        self.metrics = PerformanceMetrics()

    async def batch_insert(self, vectors: List[List[float]], metadata: List[Dict]) -> List[int]:
        """
        批量插入向量到Milvus
        优化点：将大批量分成小批次，限流插入
        """
        loop = asyncio.get_event_loop()
        total_vectors = len(vectors)
        self.metrics.total_items = total_vectors
        inserted_ids = []
        start_time = time.time()

        # 将数据分批
        batches = [
            (vectors[i:i+self.batch_size], metadata[i:i+self.batch_size])
            for i in range(0, total_vectors, self.batch_size)
        ]

        print(f"[OK] 开始批量插入: {total_vectors} 条向量, 分 {len(batches)} 批, 每批 {self.batch_size}")

        # 使用信号量控制并发
        semaphore = asyncio.Semaphore(self.max_concurrency)

        async def insert_single_batch(batch_idx: int, vectors_batch: List, metadata_batch: List):
            """插入单批数据"""
            async with semaphore:
                def _insert():
                    # 构建插入数据
                    chunk_ids = [m.get("chunk_id", 0) for m in metadata_batch]
                    contents = [m.get("content", "") for m in metadata_batch]
                    data = [chunk_ids, contents, vectors_batch]
                    result = self.collection.insert(data)
                    return result.primary_keys

                ids = await loop.run_in_executor(None, _insert)
                inserted_ids.extend(ids)

                # 打印进度
                processed = min((batch_idx + 1) * self.batch_size, total_vectors)
                print(f"    进度: {processed}/{total_vectors} ({100*processed/total_vectors:.1f}%)")

        # 创建并执行所有批次任务
        tasks = [
            insert_single_batch(idx, vectors_batch, metadata_batch)
            for idx, (vectors_batch, metadata_batch) in enumerate(batches)
        ]
        await asyncio.gather(*tasks)

        # 刷入磁盘
        await loop.run_in_executor(None, self.collection.flush)

        # 记录性能指标
        self.metrics.total_time = time.time() - start_time
        self.metrics.successful_items = len(inserted_ids)
        self.metrics.calculate()

        print(f"[OK] 批量插入完成: {len(inserted_ids)} 条向量, 耗时 {self.metrics.total_time:.2f}秒")
        return inserted_ids

    async def batch_search(
        self,
        query_vectors: List[List[float]],
        top_k: int = 5
    ) -> List[List[Dict]]:
        """
        批量搜索向量
        优化点：并发执行多个搜索请求
        """
        loop = asyncio.get_event_loop()
        total_queries = len(query_vectors)
        self.metrics.total_items = total_queries
        start_time = time.time()

        print(f"[OK] 开始批量搜索: {total_queries} 个查询, top_k={top_k}")

        # 先加载collection到内存
        await loop.run_in_executor(None, self.collection.load)

        search_params = {
            "metric_type": "IP",
            "params": {"nprobe": 10}
        }

        # 限制并发搜索数
        semaphore = asyncio.Semaphore(self.max_concurrency)

        async def search_single(query_vector: List[float], query_idx: int) -> List[Dict]:
            """执行单个搜索"""
            async with semaphore:
                def _search():
                    results = self.collection.search(
                        data=[query_vector],
                        anns_field="embedding",
                        param=search_params,
                        limit=top_k,
                        output_fields=["chunk_id", "content"]
                    )
                    hits = []
                    for hit in results[0]:
                        hits.append({
                            "id": hit.id,
                            "chunk_id": hit.entity.get("chunk_id"),
                            "content": hit.entity.get("content"),
                            "score": hit.distance
                        })
                    return hits

                return await loop.run_in_executor(None, _search)

        # 并发执行所有搜索
        tasks = [
            search_single(qv, idx)
            for idx, qv in enumerate(query_vectors)
        ]
        all_results = await asyncio.gather(*tasks)

        # 记录性能指标
        self.metrics.total_time = time.time() - start_time
        self.metrics.successful_items = total_queries
        self.metrics.calculate()

        print(f"[OK] 批量搜索完成: {total_queries} 个查询, 耗时 {self.metrics.total_time:.2f}秒")
        return all_results

# ============================================================
# 第三步：向量化器（带批处理支持）
# ============================================================
class BatchEmbedder:
    """
    支持批量处理的向量化器
    在实际项目中，这里会调用真实的embedding API
    """

    def __init__(self, dim: int = 768, batch_size: int = 100):
        self.dim = dim
        self.batch_size = batch_size

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        批量向量化文本
        模拟：分批生成随机向量
        """
        loop = asyncio.get_event_loop()
        all_vectors = []

        print(f"[OK] 开始批量向量化: {len(texts)} 条文本, 分批处理")

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]

            def _embed_batch():
                # 模拟embedding计算（实际中是API调用）
                vectors = np.random.rand(len(batch), self.dim).astype(np.float32)
                vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
                return vectors.tolist()

            vectors = await loop.run_in_executor(None, _embed_batch)
            all_vectors.extend(vectors)

            processed = min(i + self.batch_size, len(texts))
            print(f"    向量化进度: {processed}/{len(texts)}")

        return all_vectors

# ============================================================
# 第四步：完整RAG批量摄入演示
# ============================================================
async def demo_batch_ingestion():
    """演示批量摄入大量文档"""
    # 1. 连接Milvus
    connections.connect(alias="default", host="localhost", port="19530")

    # 2. 创建Collection
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="chunk_id", dtype=DataType.INT64),
        FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768)
    ]
    schema = CollectionSchema(fields=fields, description="批量RAG集合")
    collection = Collection(name="batch_rag", schema=schema)

    # 3. 准备大量文档数据（模拟）
    print("\n" + "="*60)
    print("准备模拟数据...")
    print("="*60)

    # 生成1000个模拟文档chunks
    num_chunks = 1000
    chunks = []
    for i in range(num_chunks):
        chunks.append({
            "chunk_id": i,
            "content": f"这是第 {i} 个文档块的内容，包含关于Milvus向量数据库的相关信息。",
            "metadata": {"source": f"doc_{i}"}
        })

    # 4. 向量化
    embedder = BatchEmbedder(dim=768, batch_size=200)
    texts = [c["content"] for c in chunks]
    vectors = await embedder.embed_batch(texts)

    # 5. 批量插入
    processor = BatchProcessor(collection, batch_size=500, max_concurrency=3)

    print("\n" + "="*60)
    print("开始批量插入...")
    print("="*60)
    start = time.time()
    ids = await processor.batch_insert(vectors, chunks)
    insert_time = time.time() - start

    print(f"\n插入性能: {num_chunks/insert_time:.2f} 条/秒")

    # 6. 批量搜索
    print("\n" + "="*60)
    print("开始批量搜索...")
    print("="*60)

    # 生成100个查询向量
    query_vectors = np.random.rand(100, 768).astype(np.float32)
    query_vectors = query_vectors / np.linalg.norm(query_vectors, axis=1, keepdims=True)
    query_vectors = query_vectors.tolist()

    start = time.time()
    results = await processor.batch_search(query_vectors, top_k=5)
    search_time = time.time() - start

    print(f"\n搜索性能: {100/search_time:.2f} 查询/秒")
    print(f"\n每个查询返回: {len(results[0])} 个结果")

    return processor.metrics

# ============================================================
# 主函数
# ============================================================
async def main():
    """主函数"""
    try:
        print("="*60)
        print("批量处理优化演示")
        print("="*60)

        metrics = await demo_batch_ingestion()

        print("\n" + "="*60)
        print("最终性能报告")
        print("="*60)
        print(metrics)

        print("\n[MVP-04 完成] 你已学会批量处理优化！")
        print("下一步建议：学习企业级特性 (milvus_mvp_05_enterprise.py)")

    except Exception as e:
        print(f"[错误] {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())