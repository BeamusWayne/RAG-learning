# -*- coding: utf-8 -*-
"""
GraphRAG — 基于 NetworkX 的轻量知识图谱 RAG（无需 Neo4j）
流程: 索引时: 抽取实体关系 → 构建图
      查询时: 识别实体 → 图遍历(BFS) → 子图上下文 → LLM 生成答案
"""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config as cfg
import networkx as nx
from core.llm import get_llm, get_str_chain
from core.vector_store import similarity_search
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

_GRAPH_FILE = os.path.join(cfg.GRAPH_DIR, "kg.json")

_EXTRACT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """从以下文本中抽取实体和关系，以 JSON 格式输出：
{"entities": ["实体1", "实体2", ...], "relations": [["实体1", "关系", "实体2"], ...]}
只输出 JSON，不要解释。"""),
    ("human", "{text}"),
])

_ANSWER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "你是专业问答助手。请综合以下向量检索结果与知识图谱上下文回答问题。\n\n向量上下文：\n{vector_ctx}\n\n图谱上下文：\n{graph_ctx}"),
    ("human", "{question}"),
])


def _load_graph() -> nx.Graph:
    os.makedirs(cfg.GRAPH_DIR, exist_ok=True)
    if os.path.exists(_GRAPH_FILE):
        with open(_GRAPH_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        G = nx.Graph()
        for node in data.get("nodes", []):
            G.add_node(node)
        for src, rel, tgt in data.get("edges", []):
            G.add_edge(src, tgt, relation=rel)
        return G
    return nx.Graph()


def _save_graph(G: nx.Graph):
    os.makedirs(cfg.GRAPH_DIR, exist_ok=True)
    data = {
        "nodes": list(G.nodes()),
        "edges": [[u, G[u][v].get("relation", "related"), v] for u, v in G.edges()],
    }
    with open(_GRAPH_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def index_documents(docs: list[Document]):
    """构建/更新知识图谱（在 add_documents 后调用）"""
    G = _load_graph()
    llm = get_llm()
    parser = StrOutputParser()
    for doc in docs[:20]:   # 限制初始索引量
        try:
            raw = (_EXTRACT_PROMPT | llm | parser).invoke({"text": doc.page_content[:800]})
            # 清洗 JSON
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if not match:
                continue
            parsed = json.loads(match.group())
            for entity in parsed.get("entities", []):
                G.add_node(str(entity))
            for rel in parsed.get("relations", []):
                if len(rel) == 3:
                    G.add_edge(str(rel[0]), str(rel[2]), relation=str(rel[1]))
        except Exception:
            continue
    _save_graph(G)


def _subgraph_context(G: nx.Graph, entities: list[str], max_hops: int = cfg.GRAPH_MAX_HOPS) -> str:
    if not G.nodes or not entities:
        return ""
    lines = []
    for entity in entities[:cfg.GRAPH_TOP_ENTITIES]:
        # 找最近的节点
        matched = [n for n in G.nodes if entity.lower() in n.lower()]
        for node in matched[:2]:
            try:
                neighbors = list(nx.single_source_shortest_path(G, node, cutoff=max_hops).keys())
                for nbr in neighbors[:5]:
                    if G.has_edge(node, nbr):
                        rel = G[node][nbr].get("relation", "related")
                        lines.append(f"{node} --[{rel}]--> {nbr}")
            except Exception:
                continue
    return "\n".join(lines) if lines else "（图谱中未找到相关实体）"


def _extract_entities_from_query(question: str) -> list[str]:
    """简单的实体提取：取名词短语（LLM 驱动）"""
    try:
        llm = get_llm()
        prompt = ChatPromptTemplate.from_messages([
            ("system", "从问题中提取关键实体（名词短语），每行一个，不超过5个，只输出实体列表。"),
            ("human", "{question}"),
        ])
        raw = (prompt | llm | StrOutputParser()).invoke({"question": question})
        return [e.strip() for e in raw.strip().splitlines() if e.strip()]
    except Exception:
        return question.split()[:3]


def run(question: str, **_) -> dict:
    llm = get_llm()
    parser = StrOutputParser()

    # Step 1: 向量检索（兜底）
    docs = similarity_search(question)
    vector_ctx = "\n\n".join(d.page_content for d in docs) or "（无相关资料）"

    # Step 2: 图谱检索
    G = _load_graph()
    entities = _extract_entities_from_query(question)
    graph_ctx = _subgraph_context(G, entities)

    # Step 3: 融合生成
    answer = (_ANSWER_PROMPT | llm | parser).invoke({
        "vector_ctx": vector_ctx,
        "graph_ctx": graph_ctx,
        "question": question,
    })

    return {
        "strategy": "graph",
        "answer": answer,
        "sources": [d.metadata for d in docs],
        "context_used": f"[向量]\n{vector_ctx}\n\n[图谱]\n{graph_ctx}",
        "entities": entities,
        "graph_triples": graph_ctx,
        "graph_node_count": G.number_of_nodes(),
        "steps": ["向量检索", "实体识别", f"图遍历(最大{cfg.GRAPH_MAX_HOPS}跳)", "向量+图融合生成"],
    }
