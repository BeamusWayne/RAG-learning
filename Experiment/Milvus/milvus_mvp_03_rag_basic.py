#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Milvus MVP-03: 基础RAG流程
===========================
目标：实现完整的检索增强生成(Retrieval-Augmented Generation)流程
在MVP-02异步基础上新增：

新增内容：
- 文档加载（Document Loading）
- 文档分块（Text Chunking）
- 向量化嵌入（Embedding）
- 向量存储到Milvus
- 相似性检索（Similarity Search）
- RAG提示词构建

RAG流程：
  文档 -> 分块 -> 向量化 -> Milvus存储
                                    |
  用户问题 -> 向量化 -> Milvus检索 -> 上下文片段
                                        |
                                    LLM生成回答

知识点：
- 为什么要分块：LLM有token限制，分块可以控制每个context的长度
- 为什么要检索：让LLM基于真实文档回答，避免幻觉
- 向量相似度：余弦相似度 vs 内积
"""

import asyncio
import numpy as np
from typing import List, Tuple
from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType

# ============================================================
# 第一步：文档加载器（简化版）
# ============================================================
class SimpleDocumentLoader:
    """简化版文档加载器"""
    # 在实际项目中可使用 langchain 的 DocumentLoader

    def load(self, text: str, metadata: dict = None) -> List[dict]:
        """
        将文本加载为文档列表
        返回格式: [{"content": str, "metadata": dict}]
        """
        doc = {
            "content": text.strip(),
            "metadata": metadata or {"source": "manual"}
        }
        return [doc]

    def load_from_file(self, filepath: str) -> List[dict]:
        """从文件加载文档（简化实现）"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return self.load(content, {"source": filepath})

# ============================================================
# 第二步：文档分块器
# ============================================================
class TextChunker:
    """文本分块器，将长文档分割成小块"""
    # 在实际项目中可使用 langchain 的 TextSplitter

    def __init__(self, chunk_size: int = 100, overlap: int = 20):
        """
        参数:
            chunk_size: 每块的最大字符数
            overlap: 相邻块之间的重叠字符数（保持上下文连续性）
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, documents: List[dict]) -> List[dict]:
        """
        对文档列表进行分块
        返回格式: [{"content": str, "metadata": dict, "chunk_id": int}]
        """
        chunks = []
        chunk_id = 0

        for doc in documents:
            content = doc["content"]
            metadata = doc["metadata"]

            # 如果文档比chunk_size短，直接作为一个chunk
            if len(content) <= self.chunk_size:
                chunks.append({
                    "content": content,
                    "metadata": metadata,
                    "chunk_id": chunk_id
                })
                chunk_id += 1
                continue

            # 否则滑动窗口分块
            start = 0
            while start < len(content):
                end = start + self.chunk_size
                chunk_text = content[start:end]

                chunks.append({
                    "content": chunk_text,
                    "metadata": metadata,
                    "chunk_id": chunk_id
                })
                chunk_id += 1

                # 滑动窗口，移动 chunk_size - overlap
                start += self.chunk_size - self.overlap

        print(f"[OK] 分块完成: {len(documents)} 文档 -> {len(chunks)} 块")
        return chunks

# ============================================================
# 第三步：向量化器（模拟）
# ============================================================
class MockEmbedder:
    """
    模拟向量化器，实际项目中应使用真实的embedding模型
    如：OpenAI Embedding, BGE, Sentence-BERT等
    """
    # 使用随机向量模拟embedding，实际使用时请替换为真实模型

    def __init__(self, dim: int = 768):
        """
        参数:
            dim: 向量维度，默认768（OpenAI text-embedding-ada-002的维度）
        """
        self.dim = dim

    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        将文本列表转换为向量列表
        返回: List[List[float]] - 每个文本对应的向量
        """
        # 模拟：生成随机向量（实际应用中调用embedding API）
        vectors = np.random.rand(len(texts), self.dim).astype(np.float32)
        # 归一化，使余弦相似度等于内积
        vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
        return vectors.tolist()

    def embed_query(self, query: str) -> List[float]:
        """将单个查询转换为向量"""
        return self.embed([query])[0]

# ============================================================
# 第四步：异步Milvus + RAG封装
# ============================================================
class AsyncRAG:
    """异步RAG系统，整合所有组件"""

    def __init__(self, collection_name: str = "rag_collection", dim: int = 768):
        self.collection_name = collection_name
        self.dim = dim
        self.collection = None
        self.embedder = MockEmbedder(dim=dim)
        self.chunker = TextChunker(chunk_size=100, overlap=20)
        self.loader = SimpleDocumentLoader()
        self._chunks = []  # 保存chunks用于后续检索

    async def connect(self):
        """连接到Milvus"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: connections.connect(alias="default", host="localhost", port="19530")
        )
        print(f"[OK] 连接到 Milvus")

    async def setup_collection(self):
        """创建RAG使用的Collection"""
        loop = asyncio.get_event_loop()

        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="chunk_id", dtype=DataType.INT64),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dim)
        ]
        schema = CollectionSchema(fields=fields, description="RAG向量集合")

        def _create():
            return Collection(name=self.collection_name, schema=schema)

        self.collection = await loop.run_in_executor(None, _create)
        print(f"[OK] Collection '{self.collection_name}' 创建成功")

    async def ingest(self, documents: List[dict]):
        """
         ingest: 将文档摄入到RAG系统
        流程: 文档 -> 分块 -> 向量化 -> 存入Milvus
        """
        # 1. 分块
        chunks = self.chunker.chunk(documents)
        self._chunks = chunks  # 保存以供后续检索

        # 2. 提取文本内容
        texts = [chunk["content"] for chunk in chunks]

        # 3. 向量化
        print("[OK] 开始向量化...")
        vectors = self.embedder.embed(texts)

        # 4. 存入Milvus
        loop = asyncio.get_event_loop()

        def _insert():
            data = [
                [chunk["chunk_id"] for chunk in chunks],
                texts,
                vectors
            ]
            self.collection.insert(data)
            self.collection.flush()

        await loop.run_in_executor(None, _insert)
        print(f"[OK] 文档摄入完成: {len(chunks)} 个chunks已存储")

    async def retrieve(self, query: str, top_k: int = 3) -> List[dict]:
        """
        retrieve: 根据查询检索相关文档块
        流程: 查询 -> 向量化 -> Milvus搜索 -> 返回相关片段
        """
        # 1. 将查询向量化
        query_vector = self.embedder.embed_query(query)

        # 2. 加载collection并搜索
        loop = asyncio.get_event_loop()

        await loop.run_in_executor(None, self.collection.load)

        search_params = {
            "metric_type": "IP",  # 内积相似度（向量已归一化，等同于余弦相似度）
            "params": {"nprobe": 10}
        }

        def _search():
            return self.collection.search(
                data=[query_vector],
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                output_fields=["chunk_id", "content"]
            )

        results = await loop.run_in_executor(None, _search)

        # 3. 格式化返回结果
        retrieved_chunks = []
        for hit in results[0]:
            chunk_id = hit.entity.get("chunk_id")
            content = hit.entity.get("content")
            distance = hit.distance
            retrieved_chunks.append({
                "chunk_id": chunk_id,
                "content": content,
                "score": distance
            })

        print(f"[OK] 检索完成: 找到 {len(retrieved_chunks)} 个相关片段")
        return retrieved_chunks

    def build_prompt(self, query: str, retrieved_chunks: List[dict]) -> str:
        """
        build_prompt: 构建RAG提示词
        将用户问题和检索到的上下文组合成prompt
        """
        # 构建上下文字符串
        context_parts = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            context_parts.append(f"[{i}] {chunk['content']}")

        context = "\n\n".join(context_parts)

        # 构建完整prompt
        prompt = f"""基于以下上下文信息回答用户的问题。如果上下文中没有相关信息，请如实说明。

上下文:
{context}

用户问题: {query}

请基于上下文回答:"""

        return prompt

# ============================================================
# 第五步：演示完整RAG流程
# ============================================================
async def demo_rag_flow():
    """演示完整的RAG流程"""
    # 初始化RAG系统
    rag = AsyncRAG(collection_name="demo_rag", dim=768)

    # 1. 连接并创建collection
    await rag.connect()
    await rag.setup_collection()

    # 2. 准备文档（这里使用简化的示例文档）
    documents = rag.loader.load(
        text="""
        Milvus是一个开源的向量数据库，专为高效相似性搜索而设计。
        它支持十亿级别的向量搜索，能够在毫秒级延迟下返回结果。
        Milvus广泛应用于推荐系统、图像检索，自然语言处理等领域。
        它支持多种索引类型，包括IVF、HNSW、DiskANN等。
        Milvus可以部署在本地或云端，支持Kubernetes容器化部署。
        """,
        metadata={"source": "milvus_intro"}
    )

    # 3. 摄入文档
    await rag.ingest(documents)

    # 4. 用户查询
    query = "Milvus支持哪些索引类型？"

    # 5. 检索相关片段
    retrieved_chunks = await rag.retrieve(query, top_k=2)

    # 6. 打印检索结果
    print("\n" + "="*60)
    print("检索到的相关片段:")
    print("="*60)
    for chunk in retrieved_chunks:
        print(f"[Chunk {chunk['chunk_id']}] Score: {chunk['score']:.4f}")
        print(f"内容: {chunk['content'][:100]}...")
        print("-"*40)

    # 7. 构建提示词
    prompt = rag.build_prompt(query, retrieved_chunks)
    print("\n" + "="*60)
    print("构建的提示词 (可发送给LLM):")
    print("="*60)
    print(prompt)

    return rag, retrieved_chunks

# ============================================================
# 主函数
# ============================================================
async def main():
    """主函数"""
    try:
        print("="*60)
        print("RAG 基础流程演示")
        print("="*60)

        rag, chunks = await demo_rag_flow()

        print("\n[MVP-03 完成] 你已学会基础RAG流程！")
        print("下一步建议：学习批量处理优化 (milvus_mvp_04_batch.py)")

    except Exception as e:
        print(f"[错误] {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())