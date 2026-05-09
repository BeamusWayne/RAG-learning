#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Milvus MVP-02: 异步Milvus客户端
===============================
目标：在MVP-01基础上添加异步支持，实现非阻塞的Milvus操作
新增内容：
- asyncio异步编程基础
- async/await语法
- 并发执行多个Milvus操作

知识点：
- 为什么需要异步：在高并发场景下，异步可以显著提升吞吐量
- asyncio事件循环机制
- async with上下文管理器
"""

import asyncio
import numpy as np
from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType

# ============================================================
# 第一步：定义异步连接管理器
# ============================================================
class AsyncMilvusConnection:
    """异步Milvus连接管理器，使用上下文管理器"""

    def __init__(self, host="localhost", port="19530", alias="default"):
        self.host = host
        self.port = port
        self.alias = alias

    async def __aenter__(self):
        """进入上下文时连接Milvus"""
        # 注意：pymilvus本身是同步库，这里使用loop.run_in_executor避免阻塞
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: connections.connect(alias=self.alias, host=self.host, port=self.port)
        )
        print(f"[OK] 异步连接到 Milvus ({self.host}:{self.port})")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时断开连接"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: connections.disconnect(alias=self.alias))
        print("[OK] Milvus连接已关闭")

# ============================================================
# 第二步：异步Collection操作
# ============================================================
class AsyncCollection:
    """异步Collection封装，提供非阻塞的Milvus操作"""

    def __init__(self, name: str, dim: int = 128):
        self.name = name
        self.dim = dim
        self._collection = None

    async def create(self):
        """异步创建Collection"""
        loop = asyncio.get_event_loop()
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dim)
        ]
        schema = CollectionSchema(fields=fields, description="异步向量集合")

        def _create():
            return Collection(name=self.name, schema=schema)

        self._collection = await loop.run_in_executor(None, _create)
        print(f"[OK] Collection '{self.name}' 创建成功 (dim={self.dim})")
        return self._collection

    async def insert(self, vectors: list):
        """异步插入向量"""
        loop = asyncio.get_event_loop()

        def _insert():
            result = self._collection.insert([vectors])
            self._collection.flush()
            return result

        insert_result = await loop.run_in_executor(None, _insert)
        print(f"[OK] 插入 {len(vectors)} 条向量完成")
        return insert_result.primary_keys

    async def search(self, query_vector: list, top_k: int = 3):
        """异步搜索向量"""
        loop = asyncio.get_event_loop()

        # 先加载到内存
        await loop.run_in_executor(None, self._collection.load)

        search_params = {
            "metric_type": "IP",
            "params": {"nprobe": 10}
        }

        def _search():
            return self._collection.search(
                data=[query_vector],
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                output_fields=["id"]
            )

        results = await loop.run_in_executor(None, _search)
        print(f"[OK] 搜索完成，找到 {len(results[0])} 条相似向量")
        return results

    async def batch_insert(self, batch_vectors: list, batch_size: int = 100):
        """批量插入向量（分批处理避免内存峰值）"""
        total = 0
        for i in range(0, len(batch_vectors), batch_size):
            batch = batch_vectors[i:i + batch_size]
            await self.insert(batch)
            total += len(batch)
        print(f"[OK] 批量插入完成，共计 {total} 条向量")

    def get_collection(self):
        """获取底层collection对象"""
        return self._collection

# ============================================================
# 第三步：演示并发操作
# ============================================================
async def demo_concurrent_search(collection: AsyncCollection):
    """并发执行多个搜索请求"""
    # 生成多个不同的查询向量
    query_vectors = np.random.rand(5, 128).astype(np.float32).tolist()

    # 使用asyncio.gather并发执行所有搜索
    tasks = [collection.search(qv, top_k=3) for qv in query_vectors]
    results = await asyncio.gather(*tasks)
    print(f"[OK] 并发搜索完成，共 {len(results)} 个结果集")
    return results

# ============================================================
# 第四步：演示批量操作
# ============================================================
async def demo_batch_operations(collection: AsyncCollection, num_vectors: int = 100):
    """演示批量插入操作"""
    # 生成100条随机向量
    vectors = np.random.rand(num_vectors, 128).astype(np.float32).tolist()

    # 批量插入
    await collection.batch_insert(vectors, batch_size=20)
    print(f"[OK] 批量操作演示完成")

# ============================================================
# 主函数
# ============================================================
async def main():
    """异步主函数"""
    try:
        # 1. 异步连接
        async with AsyncMilvusConnection() as conn:
            # 2. 创建Collection
            collection = AsyncCollection(name="async_demo", dim=128)
            await collection.create()

            # 3. 单次插入和搜索
            single_vector = np.random.rand(128).astype(np.float32).tolist()
            await collection.insert([single_vector])
            await collection.search(single_vector, top_k=3)

            # 4. 批量操作
            await demo_batch_operations(collection, num_vectors=50)

            # 5. 并发搜索
            await demo_concurrent_search(collection)

            print("\n[MVP-02 完成] 恭喜你学会了异步Milvus操作！")
            print("下一步建议：学习基础RAG流程 (milvus_mvp_03_rag_basic.py)")

    except Exception as e:
        print(f"[错误] {e}")
        raise

if __name__ == "__main__":
    # Python 3.7+ 支持直接使用asyncio.run()
    asyncio.run(main())