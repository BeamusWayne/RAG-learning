#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Milvus MVP-01: 同步最简Milvus连接
===============================
目标：学习Milvus最基本的连接、创建collection、插入向量和搜索操作
适用场景：理解Milvus核心概念，无需关心异步和性能优化

知识点：
- Milvus连接方式（localhost:19530）
- Collection创建和schema定义
- 插入向量和搜索向量的基本API
"""

from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType
import numpy as np

# ============================================================
# 第一步：连接到Milvus服务
# ============================================================
def connect_milvus():
    """连接到Milvus服务"""
    # Milvus默认连接地址是localhost:19530
    # 如果使用Docker部署Milvus，确保端口映射正确
    connections.connect(
        alias="default",
        host="localhost",
        port="19530"
    )
    print("[OK] Milvus连接成功")

# ============================================================
# 第二步：创建Collection（集合）
# ============================================================
def create_collection():
    """创建包含向量字段的Collection"""
    # 定义collection的schema
    # - id: 主键字段，用于唯一标识每条记录
    # - embedding: 向量字段，维度为128（可根据实际模型调整）
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=128)
    ]
    schema = CollectionSchema(fields=fields, description="简单的向量集合")

    # 创建collection（如果已存在则跳过）
    collection = Collection(name="demo_collection", schema=schema)
    print("[OK] Collection 'demo_collection' 创建成功")
    return collection

# ============================================================
# 第三步：插入向量数据
# ============================================================
def insert_vectors(collection, num_vectors=10):
    """向collection中插入随机向量"""
    # 生成随机向量数据
    # 在实际应用中，这些向量通常来自 embedding 模型（如 OpenAI、BGE 等）
    vectors = np.random.rand(num_vectors, 128).astype(np.float32).tolist()

    # 插入数据并获取返回的主键列表
    insert_result = collection.insert([vectors])
    print(f"[OK] 成功插入 {num_vectors} 条向量")

    # 将数据刷入磁盘，确保数据持久化
    collection.flush()
    return insert_result.primary_keys

# ============================================================
# 第四步：搜索相似向量
# ============================================================
def search_vectors(collection, query_vector=None, top_k=3):
    """搜索与给定向量最相似的top_k条记录"""
    # 加载collection到内存，以便进行搜索
    collection.load()

    # 如果没有提供查询向量，随机生成一个
    if query_vector is None:
        query_vector = np.random.rand(128).astype(np.float32).tolist()

    # 定义搜索参数
    # - anns_field: 指定要搜索的向量字段
    # - param: 搜索参数，IP表示使用内积相似度
    # - limit: 返回的最相似结果数量
    search_params = {
        "metric_type": "IP",  # 内积相似度（Inner Product）
        "params": {"nprobe": 10}
    }

    # 执行搜索
    results = collection.search(
        data=[query_vector],
        anns_field="embedding",
        param=search_params,
        limit=top_k,
        output_fields=["id"]
    )

    print(f"[OK] 搜索完成，找到 {len(results[0])} 条相似向量")
    for i, hit in enumerate(results[0]):
        print(f"    Top-{i+1}: ID={hit.id}, 距离={hit.distance:.4f}")

    return results

# ============================================================
# 第五步：资源清理
# ============================================================
def cleanup(collection):
    """删除collection释放资源"""
    # 删除collection（生产环境中请谨慎操作）
    Collection(name="demo_collection").drop()
    print("[OK] Collection 已删除")

# ============================================================
# 主函数 - 串联所有步骤
# ============================================================
def main():
    """主函数：串联MVP的所有步骤"""
    try:
        # 1. 连接
        connect_milvus()

        # 2. 创建Collection
        collection = create_collection()

        # 3. 插入向量
        ids = insert_vectors(collection, num_vectors=10)

        # 4. 搜索向量
        search_vectors(collection, top_k=3)

        # 5. 清理（可选，取消注释即可执行）
        # cleanup(collection)

        print("\n[MVP-01 完成] 恭喜你完成了Milvus最基本的操作！")
        print("下一步建议：学习异步版本的实现 (milvus_mvp_02_async.py)")

    except Exception as e:
        print(f"[错误] {e}")
        raise

if __name__ == "__main__":
    main()