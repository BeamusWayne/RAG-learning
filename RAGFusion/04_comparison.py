"""
Step 4 — 三方对比：Naive RAG vs HyDE vs RAG Fusion
=====================================================
把三种 Query Transformation 技术放在同一知识库、同一问题下对比：

  Naive RAG   : embed(问题)        → 检索 → 答案
  HyDE        : embed(假设文档)    → 检索 → 答案
  RAG Fusion  : N 路检索 + RRF 融合 → 答案

对比维度：
  - 检索到的文档集合（有无重叠？各自独特发现了什么？）
  - 最终答案质量（主观判断）
  - API 调用次数（成本视角）

运行：
  export OPENAI_API_KEY=...
  uv run python 04_comparison.py
"""

import os
from dataclasses import dataclass, field

import numpy as np
from openai import OpenAI

CHAT_MODEL = "gpt-5.4"
EMBEDDING_MODEL = "text-embedding-ada-002"
TOP_K = 3
NUM_QUERIES = 3   # RAG Fusion 子查询数（少一点节省调用）
RRF_K = 60

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


# ── 共用组件 ──────────────────────────────────────────────────────────────────
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

    def search(self, query: str, top_k: int = TOP_K) -> list[str]:
        q = np.array(self._embed(query))
        scores = [
            float(np.dot(q, np.array(e)) / (np.linalg.norm(q) * np.linalg.norm(e) + 1e-8))
            for e in self.embeddings
        ]
        top_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        return [self.docs[i] for i in top_idx]


@dataclass
class RRFFusion:
    k: int = RRF_K
    scores: dict[str, float] = field(default_factory=dict)

    def add_ranked_list(self, docs: list[str]) -> None:
        for rank, doc in enumerate(docs, start=1):
            self.scores[doc] = self.scores.get(doc, 0.0) + 1.0 / (self.k + rank)

    def top_k(self, k: int) -> list[str]:
        return [d for d, _ in sorted(self.scores.items(), key=lambda x: x[1], reverse=True)[:k]]


def chat(client: OpenAI, prompt: str) -> str:
    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content.strip()


def generate_answer(client: OpenAI, question: str, docs: list[str]) -> str:
    context = "\n".join(f"- {d}" for d in docs)
    return chat(client, f"请根据以下资料回答问题。\n\n资料：\n{context}\n\n问题：{question}\n\n答案：")


# ── 三种方法 ──────────────────────────────────────────────────────────────────
def naive_rag(
    client: OpenAI, store: SimpleVectorStore, question: str
) -> tuple[list[str], str, int]:
    """LLM 调用次数：1（生成答案）"""
    retrieved = store.search(question)
    answer = generate_answer(client, question, retrieved)
    return retrieved, answer, 1


def hyde_rag(
    client: OpenAI, store: SimpleVectorStore, question: str
) -> tuple[str, list[str], str, int]:
    """LLM 调用次数：2（生成假设文档 + 生成答案）"""
    hypothesis = chat(
        client,
        f"请为下面的问题写一段技术文档片段（2-4句话），用于检索。\n问题：{question}\n假设文档：",
    )
    retrieved = store.search(hypothesis)
    answer = generate_answer(client, question, retrieved)
    return hypothesis, retrieved, answer, 2


def rag_fusion(
    client: OpenAI, store: SimpleVectorStore, question: str, n: int = NUM_QUERIES
) -> tuple[list[str], list[str], str, int]:
    """LLM 调用次数：2（查询扩展 + 生成答案）"""
    raw = chat(
        client,
        f"请把下面的问题改写成 {n} 个不同搜索查询，每行一条，不加编号。\n问题：{question}",
    )
    queries = [l.strip() for l in raw.splitlines() if l.strip()][:n]

    fusion = RRFFusion()
    for q in queries:
        fusion.add_ranked_list(store.search(q))
    fused = fusion.top_k(TOP_K)

    answer = generate_answer(client, question, fused)
    return queries, fused, answer, 2


# ── 对比报告 ──────────────────────────────────────────────────────────────────
def overlap_report(
    naive_docs: list[str],
    hyde_docs: list[str],
    fusion_docs: list[str],
) -> None:
    sets = {
        "Naive": set(naive_docs),
        "HyDE": set(hyde_docs),
        "Fusion": set(fusion_docs),
    }
    print("  文档重叠矩阵：")
    pairs = [("Naive", "HyDE"), ("Naive", "Fusion"), ("HyDE", "Fusion")]
    for a, b in pairs:
        shared = len(sets[a] & sets[b])
        print(f"    {a} ∩ {b} = {shared} 条")

    union = sets["Naive"] | sets["HyDE"] | sets["Fusion"]
    print(f"\n  三方合计覆盖不同文档：{len(union)} 条（知识库共 {len(DOCUMENTS)} 条）")

    all_three = sets["Naive"] & sets["HyDE"] & sets["Fusion"]
    if all_three:
        print(f"  三方共同命中（最重要）：")
        for d in all_three:
            print(f"    → {d}")

    unique = {
        name: s - (union - s)
        for name, s in sets.items()
    }
    for name, u in unique.items():
        if u:
            print(f"  仅 {name} 独有：")
            for d in u:
                print(f"    → {d}")


def sep(title: str) -> None:
    print(f"\n{'═' * 57}")
    print(f"  {title}")
    print(f"{'═' * 57}")


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

    question = input("请输入问题（直接回车使用默认）：").strip()
    if not question:
        question = "提升 RAG 检索效果有哪些技术方案？"
    print(f"\n问题：{question}")

    # ── 执行三种方法 ──────────────────────────────────────────────────────
    print("\n正在运行 Naive RAG...")
    naive_docs, naive_ans, naive_calls = naive_rag(client, store, question)

    print("正在运行 HyDE...")
    hypothesis, hyde_docs, hyde_ans, hyde_calls = hyde_rag(client, store, question)

    print("正在运行 RAG Fusion...")
    queries, fusion_docs, fusion_ans, fusion_calls = rag_fusion(client, store, question)

    # ── 打印结果 ──────────────────────────────────────────────────────────
    sep("Naive RAG")
    print(f"API 调用：{naive_calls} 次")
    print("检索文档：")
    for i, d in enumerate(naive_docs, 1):
        print(f"  [{i}] {d}")
    print(f"\n答案：\n{naive_ans}")

    sep("HyDE RAG")
    print(f"API 调用：{hyde_calls} 次")
    print(f"假设文档：\n  {hypothesis}\n")
    print("检索文档：")
    for i, d in enumerate(hyde_docs, 1):
        print(f"  [{i}] {d}")
    print(f"\n答案：\n{hyde_ans}")

    sep("RAG Fusion")
    print(f"API 调用：{fusion_calls} 次")
    print("扩展查询：")
    for i, q in enumerate(queries, 1):
        print(f"  [{i}] {q}")
    print("\nRRF 融合后 Top 文档：")
    for i, d in enumerate(fusion_docs, 1):
        print(f"  [{i}] {d}")
    print(f"\n答案：\n{fusion_ans}")

    sep("对比分析")
    overlap_report(naive_docs, hyde_docs, fusion_docs)
    print(f"\n  成本对比：Naive={naive_calls} 次 | HyDE={hyde_calls} 次 | Fusion={fusion_calls} 次")
    print("  （成本相近，但 Fusion 检索覆盖面更广）")


if __name__ == "__main__":
    main()
