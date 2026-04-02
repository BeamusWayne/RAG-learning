import numpy as np
from openai import OpenAI
from langchain_community.embeddings import DashScopeEmbeddings

# ── 配置 ─────────────────────────────────────────────────────────────────────
BASE_URL   = ""
API_KEY    = ""
CHAT_MODEL = "gpt-5.4"

# ── 客户端 ────────────────────────────────────────────────────────────────────
client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

# ── Embedding（DashScope text-embedding-v1） ──────────────────────────────────
embedder = DashScopeEmbeddings(
    model="text-embedding-v1",
    dashscope_api_key=API_KEY,
)


# ── 向量库 ────────────────────────────────────────────────────────────────────
class SimpleVectorStore:
    def __init__(self):
        self.docs = []
        self.embeddings = []

    def add_document(self, text: str):
        emb = embedder.embed_query(text)
        self.docs.append(text)
        self.embeddings.append(emb)

    @staticmethod
    def _cosine(a, b):
        a, b = np.array(a), np.array(b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)

    def search(self, query: str, top_k: int = 3):
        query_emb = embedder.embed_query(query)
        sims = [self._cosine(query_emb, emb) for emb in self.embeddings]
        indices = sorted(range(len(sims)), key=lambda i: sims[i], reverse=True)[:top_k]
        return [self.docs[i] for i in indices]


# ── Agentic RAG ───────────────────────────────────────────────────────────────
class AgenticRAG:
    def __init__(self):
        self.vs = SimpleVectorStore()

    def add_knowledge(self, document_list):
        for doc in document_list:
            self.vs.add_document(doc)

    def agentic_reasoning(self, query: str, context: str) -> str:
        prompt = (
            "你是一个AI助手，可以基于知识库做agentic推理。\n"
            f"问题：{query}\n"
            f"已知信息：\n{context}\n"
            "请详细解析并作答："
        )
        r = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return r.choices[0].message.content.strip()

    def ask(self, query: str) -> str:
        context_docs = self.vs.search(query)
        context = "\n".join(context_docs)
        return self.agentic_reasoning(query, context)


# ── 入口 ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    rag = AgenticRAG()
    documents = [
        "北京是中国的首都。",
        "上海是中国最大的城市之一。",
        "长城是中国著名的历史遗迹。",
    ]
    rag.add_knowledge(documents)
    user_query = input("请输入你的问题：")
    result = rag.ask(user_query)
    print("AgenticRAG答复：")
    print(result)
