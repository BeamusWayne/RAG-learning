"""
Step 3 — 完整 RAG Fusion Pipeline
====================================
把前两步组合成完整流程：
  1. 查询扩展：一个问题 → N 个子查询
  2. 并行检索：每个子查询独立检索向量库
  3. RRF 融合：合并 N 路结果，得到统一排序
  4. 生成答案：用融合后的 Top-K 文档生成最终答案

运行：
  export OPENAI_API_KEY=...
  export OPENAI_BASE_URL=...   # 可选
  uv run python 03_rag_fusion_pipeline.py
"""

import os
from dataclasses import dataclass, field

import numpy as np
from openai import OpenAI

CHAT_MODEL = "gpt-5.4"
EMBEDDING_MODEL = "text-embedding-ada-002"
NUM_QUERIES = 4   # 扩展子查询数量
TOP_K = 3         # 每路检索返回 Top-K
RRF_K = 60        # RRF 平滑常数

DOCUMENTS = [
    "向量数据库通过高维向量索引实现语义检索，常见实现有 Chroma、Pinecone、Weaviate。",
    "Chroma 是一个开源的本地向量数据库，支持 Python 直接调用，适合快速原型开发。",
    "余弦相似度衡量两个向量的夹角，值越接近 1 代表语义越相似。",
    "文档分块（Chunking）是 RAG 的关键步骤：块太大引入噪声，块太小丢失上下文。",
    "Top-K 检索从向量库里找出与查询最相似的 K 个片段，作为上下文喂给 LLM。",
    "FAISS 是 Meta 开源的高效近似最近邻搜索库，适合大规模向量检索场景。",
    "Embedding 模型将文本映射到稠密向量空间，使语义相近的文本距离更近。",
    "RAG 将检索到的外部知识注入 LLM prompt，减少幻觉，提高事实准确性。",
    "重排序（Reranking）在 Top-K 检索后用 Cross-Encoder 对结果精排，提升精度。",
    "混合检索结合 BM25（关键词）和向量检索（语义），互补提升召回率。",
    "查询改写将用户模糊问题转化为更适合检索的表述，提高命中率。",
    "HyDE 先生成假设文档再用其 embedding 检索，解决问题与文档风格不对齐问题。",
]


# ── 向量库 ────────────────────────────────────────────────────────────────────
class SimpleVectorStore:
    def __init__(self, client: OpenAI) -> None:
        self.client = client
        self.docs: list[str] = []
        self.embeddings: list[list[float]] = []

    def _embed(self, text: str) -> list[float]:
        resp = self.client.embeddings.create(input=text, model=EMBEDDING_MODEL)
        return resp.data[0].embedding

    def add(self, text: str) -> None:
        self.docs.append(text)
        self.embeddings.append(self._embed(text))

    def search(self, query: str, top_k: int = TOP_K) -> list[tuple[str, float]]:
        """返回 (doc, score) 列表，按相似度降序。"""
        q_emb = np.array(self._embed(query))
        scores = [
            float(
                np.dot(q_emb, np.array(e))
                / (np.linalg.norm(q_emb) * np.linalg.norm(e) + 1e-8)
            )
            for e in self.embeddings
        ]
        top_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        return [(self.docs[i], scores[i]) for i in top_idx]


# ── RRF 融合 ──────────────────────────────────────────────────────────────────
@dataclass
class RRFFusion:
    k: int = RRF_K
    scores: dict[str, float] = field(default_factory=dict)

    def add_ranked_list(self, ranked_docs: list[str]) -> None:
        for rank, doc in enumerate(ranked_docs, start=1):
            self.scores[doc] = self.scores.get(doc, 0.0) + 1.0 / (self.k + rank)

    def top_k(self, k: int) -> list[str]:
        ranked = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in ranked[:k]]


# ── RAG Fusion Pipeline ───────────────────────────────────────────────────────
class RAGFusionPipeline:
    def __init__(self, client: OpenAI, store: SimpleVectorStore) -> None:
        self.client = client
        self.store = store

    def expand_queries(self, question: str, n: int = NUM_QUERIES) -> list[str]:
        """Step 1：把原始问题扩展成 n 个子查询。"""
        prompt = (
            f"请把下面的问题改写成 {n} 个不同角度的搜索查询，"
            "覆盖不同关键词和表述方式。\n"
            "直接输出查询列表，每行一条，不加编号。\n\n"
            f"原始问题：{question}"
        )
        resp = self.client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
        )
        lines = resp.choices[0].message.content.strip().splitlines()
        return [l.strip() for l in lines if l.strip()][:n]

    def retrieve_all(
        self, queries: list[str], top_k: int = TOP_K
    ) -> dict[str, list[tuple[str, float]]]:
        """Step 2：用每个子查询独立检索，返回 {查询: [(doc, score), ...]}。"""
        return {q: self.store.search(q, top_k=top_k) for q in queries}

    def fuse(
        self, all_results: dict[str, list[tuple[str, float]]], final_k: int = TOP_K
    ) -> list[str]:
        """Step 3：RRF 融合所有检索结果。"""
        fusion = RRFFusion()
        for ranked_with_scores in all_results.values():
            ranked_docs = [doc for doc, _ in ranked_with_scores]
            fusion.add_ranked_list(ranked_docs)
        return fusion.top_k(final_k)

    def generate(self, question: str, context_docs: list[str]) -> str:
        """Step 4：用融合后的文档生成最终答案。"""
        context = "\n".join(f"- {d}" for d in context_docs)
        prompt = (
            f"请根据以下资料回答问题。\n\n资料：\n{context}\n\n问题：{question}\n\n答案："
        )
        resp = self.client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content.strip()

    def ask(self, question: str) -> dict:
        """完整 RAG Fusion 流程，返回中间结果供调试。"""
        queries = self.expand_queries(question)
        all_results = self.retrieve_all(queries)
        fused_docs = self.fuse(all_results)
        answer = self.generate(question, fused_docs)
        return {
            "question": question,
            "queries": queries,
            "all_results": all_results,
            "fused_docs": fused_docs,
            "answer": answer,
        }


# ── 主程序 ────────────────────────────────────────────────────────────────────
def main() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("请先设置环境变量 OPENAI_API_KEY。")

    kwargs: dict = {}
    if base := os.environ.get("OPENAI_BASE_URL"):
        kwargs["base_url"] = base
    client = OpenAI(**kwargs)

    print("正在构建知识库...")
    store = SimpleVectorStore(client)
    for doc in DOCUMENTS:
        store.add(doc)
    print(f"已写入 {len(DOCUMENTS)} 条文档。\n")

    pipeline = RAGFusionPipeline(client, store)

    question = input("请输入问题（直接回车使用默认）：").strip()
    if not question:
        question = "RAG 系统检索效果不好，有哪些优化方向？"

    print(f"\n问题：{question}\n")
    result = pipeline.ask(question)

    # ── 打印每一步的中间结果 ──────────────────────────────────────────────
    print("─" * 55)
    print("Step 1 — 扩展的子查询")
    print("─" * 55)
    for i, q in enumerate(result["queries"], 1):
        print(f"  [{i}] {q}")

    print("\n─" * 1 + "─" * 54)
    print("Step 2 — 每路检索结果")
    print("─" * 55)
    for q, docs_scores in result["all_results"].items():
        print(f"\n  查询：{q}")
        for rank, (doc, score) in enumerate(docs_scores, 1):
            print(f"    #{rank} [{score:.3f}] {doc}")

    print("\n─" * 1 + "─" * 54)
    print("Step 3 — RRF 融合后 Top 文档")
    print("─" * 55)
    for i, doc in enumerate(result["fused_docs"], 1):
        print(f"  [{i}] {doc}")

    print("\n─" * 1 + "─" * 54)
    print("Step 4 — 最终答案")
    print("─" * 55)
    print(result["answer"])


if __name__ == "__main__":
    main()
