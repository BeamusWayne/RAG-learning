import os

from openai import OpenAI

# 对话模型：OpenAI 平台模型 ID（见官方文档）
CHAT_MODEL = "gpt-5.4"
EMBEDDING_MODEL = "text-embedding-ada-002"




# Embeddings Models
from langchain_community.embeddings import DashScopeEmbeddings

#初始化嵌入模型对象，其默认使用模型是：text-embedding-v1
embed = DashScopeEmbeddings()



def _make_client() -> OpenAI:
    kwargs = {}
    base = os.environ.get("OPENAI_BASE_URL")
    if base:
        kwargs["base_url"] = base
    return OpenAI(**kwargs)


class SimpleVectorStore:
    def __init__(self, client: OpenAI):
        self.client = client
        self.docs = []
        self.embeddings = []

    def embed(self, text: str):
        r = self.client.embeddings.create(
            input=text,
            model=EMBEDDING_MODEL,
        )
        return r.data[0].embedding

    def add_document(self, text):
        emb = self.embed(text)
        self.docs.append(text)
        self.embeddings.append(emb)

    def similarity(self, emb1, emb2):
        import numpy as np

        emb1 = np.array(emb1)
        emb2 = np.array(emb2)
        return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2) + 1e-8)

    def search(self, query, top_k=3):
        query_emb = self.embed(query)
        sims = [self.similarity(query_emb, emb) for emb in self.embeddings]
        indices = sorted(range(len(sims)), key=lambda i: sims[i], reverse=True)[:top_k]
        return [self.docs[i] for i in indices]


class AgenticRAG:
    def __init__(self, client: OpenAI):
        self.client = client
        self.vs = SimpleVectorStore(client)

    def add_knowledge(self, document_list):
        for doc in document_list:
            self.vs.add_document(doc)

    def agentic_reasoning(self, query, context):
        prompt = (
            "你是一个AI助手，可以基于知识库做agentic推理。\n"
            f"问题：{query}\n"
            f"已知信息：\n{context}\n"
            "请详细解析并作答："
        )
        r = self.client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return r.choices[0].message.content.strip()

    def ask(self, query):
        context_docs = self.vs.search(query)
        context = "\n".join(context_docs)
        return self.agentic_reasoning(query, context)


if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit(
            "请设置环境变量 OPENAI_API_KEY。\n"
            "可选：OPENAI_BASE_URL（兼容 OpenAI 格式的第三方网关）。"
        )

    client = _make_client()
    rag = AgenticRAG(client)
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
