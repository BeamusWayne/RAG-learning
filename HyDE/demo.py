"""
HyDE（Hypothetical Document Embeddings）MVP
============================================
核心思路：
  Naive RAG : embed(用户问题)         → 检索 → 生成答案
  HyDE RAG  : embed(假设答案) → 检索 → 生成答案
              └── 先让 LLM 生成一个"假设文档"，用它的 embedding 检索

为什么有效？
  问题和文档在向量空间里通常不对齐。
  假设答案的语言风格更接近知识库里的文档，检索命中率更高。

运行：
  export OPENAI_API_KEY=...
  export OPENAI_BASE_URL=...   # 可选，兼容第三方网关
  uv run python demo.py
"""

import os

import numpy as np
from openai import OpenAI

CHAT_MODEL = "gpt-5.4"
EMBEDDING_MODEL = "text-embedding-ada-002"

# ── 知识库：模拟一份技术文档 ────────────────────────────────────────────────
DOCUMENTS = [
    "向量数据库（Vector Database）通过高维向量索引实现语义检索，常见实现有 Chroma、Pinecone、Weaviate。",
    "Chroma 是一个开源的本地向量数据库，支持 Python 直接调用，适合快速原型开发。",
    "余弦相似度（Cosine Similarity）衡量两个向量的夹角，值越接近 1 代表语义越相似。",
    "文档分块（Chunking）是 RAG 的关键步骤：块太大引入噪声，块太小丢失上下文。",
    "Top-K 检索从向量库里找出与查询最相似的 K 个文档片段，作为上下文喂给 LLM。",
    "FAISS 是 Meta 开源的高效近似最近邻搜索库，适合大规模向量检索场景。",
    "Embedding 模型将文本映射到稠密向量空间，使语义相近的文本在空间中距离更近。",
    "RAG（Retrieval-Augmented Generation）将检索到的外部知识注入 LLM prompt，减少幻觉。",
]


# ── 向量库（纯 NumPy，无需外部服务）────────────────────────────────────────
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

    def search(self, query: str, top_k: int = 3) -> list[str]:
        q_emb = np.array(self._embed(query))
        scores = [
            np.dot(q_emb, np.array(e))
            / (np.linalg.norm(q_emb) * np.linalg.norm(e) + 1e-8)
            for e in self.embeddings
        ]
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[
            :top_k
        ]
        return [self.docs[i] for i in top_indices]


# ── Naive RAG ────────────────────────────────────────────────────────────────
class NaiveRAG:
    """直接用用户问题 embedding 检索，然后生成答案。"""

    def __init__(self, client: OpenAI, store: SimpleVectorStore) -> None:
        self.client = client
        self.store = store

    def ask(self, question: str, top_k: int = 3) -> tuple[list[str], str]:
        # 1. 用问题直接检索
        retrieved = self.store.search(question, top_k=top_k)

        # 2. 生成最终答案
        context = "\n".join(f"- {d}" for d in retrieved)
        prompt = (
            f"请根据以下资料回答问题。\n\n资料：\n{context}\n\n问题：{question}\n\n答案："
        )
        resp = self.client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return retrieved, resp.choices[0].message.content.strip()


# ── HyDE RAG ─────────────────────────────────────────────────────────────────
class HyDeRAG:
    """
    两步流程：
      Step 1  →  让 LLM 生成一个「假设文档」（不看知识库，只靠模型内部知识）
      Step 2  →  用假设文档的 embedding 检索真实知识库
      Step 3  →  把真实检索结果 + 原始问题送给 LLM 生成最终答案
    """

    def __init__(self, client: OpenAI, store: SimpleVectorStore) -> None:
        self.client = client
        self.store = store

    def _generate_hypothesis(self, question: str) -> str:
        """Step 1：生成假设文档。"""
        prompt = (
            "请为下面的问题写一段简短的技术文档片段（2-4句话），"
            "就像这段话出自一本技术书籍或官方文档。"
            "不需要完全准确，目的是生成一个用于检索的假设文档。\n\n"
            f"问题：{question}\n\n假设文档："
        )
        resp = self.client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()

    def ask(self, question: str, top_k: int = 3) -> tuple[str, list[str], str]:
        # Step 1：生成假设文档
        hypothesis = self._generate_hypothesis(question)

        # Step 2：用假设文档 embedding 检索真实知识库
        retrieved = self.store.search(hypothesis, top_k=top_k)

        # Step 3：用原始问题 + 真实检索结果生成最终答案
        context = "\n".join(f"- {d}" for d in retrieved)
        prompt = (
            f"请根据以下资料回答问题。\n\n资料：\n{context}\n\n问题：{question}\n\n答案："
        )
        resp = self.client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return hypothesis, retrieved, resp.choices[0].message.content.strip()


# ── 工具函数 ──────────────────────────────────────────────────────────────────
def separator(title: str) -> None:
    print(f"\n{'─' * 55}")
    print(f"  {title}")
    print(f"{'─' * 55}")


# ── 主程序：对比演示 ──────────────────────────────────────────────────────────
def main() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit(
            "请先设置环境变量 OPENAI_API_KEY。\n"
            "可选：OPENAI_BASE_URL（兼容 OpenAI 格式的第三方网关）。"
        )

    kwargs: dict = {}
    if base := os.environ.get("OPENAI_BASE_URL"):
        kwargs["base_url"] = base
    client = OpenAI(**kwargs)

    # 构建共享知识库
    print("正在构建知识库（embedding 中...）")
    store = SimpleVectorStore(client)
    for doc in DOCUMENTS:
        store.add(doc)
    print(f"已写入 {len(DOCUMENTS)} 条文档。\n")

    naive = NaiveRAG(client, store)
    hyde = HyDeRAG(client, store)

    question = input("请输入你的问题（直接回车使用默认问题）：").strip()
    if not question:
        question = "怎么选择合适的向量数据库？"
    print(f"\n问题：{question}")

    # ── Naive RAG ──
    separator("Naive RAG（直接用问题检索）")
    naive_retrieved, naive_answer = naive.ask(question)
    print("检索到的文档：")
    for i, doc in enumerate(naive_retrieved, 1):
        print(f"  [{i}] {doc}")
    print(f"\n最终答案：\n{naive_answer}")

    # ── HyDE RAG ──
    separator("HyDE RAG（先生成假设文档再检索）")
    hypothesis, hyde_retrieved, hyde_answer = hyde.ask(question)
    print(f"生成的假设文档：\n  {hypothesis}\n")
    print("用假设文档检索到的文档：")
    for i, doc in enumerate(hyde_retrieved, 1):
        print(f"  [{i}] {doc}")
    print(f"\n最终答案：\n{hyde_answer}")

    # ── 检索差异对比 ──
    separator("检索结果对比")
    naive_set = set(naive_retrieved)
    hyde_set = set(hyde_retrieved)
    only_naive = naive_set - hyde_set
    only_hyde = hyde_set - naive_set
    shared = naive_set & hyde_set

    print(f"共同命中：{len(shared)} 条")
    print(f"仅 Naive 命中：{len(only_naive)} 条")
    print(f"仅 HyDE  命中：{len(only_hyde)} 条")
    if only_hyde:
        print("\nHyDE 额外发现的文档（Naive 错过的）：")
        for doc in only_hyde:
            print(f"  → {doc}")


if __name__ == "__main__":
    main()
