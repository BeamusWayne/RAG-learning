# -*- coding: utf-8 -*-
"""
意图路由器 — 识别用户意图并选择最合适的 RAG 策略
策略选择逻辑:
  - 事实查询 / 定义      → baseline
  - 需要推理 / 多跳问题   → graph
  - 复杂分析 / 不确定性高 → crag
  - 模糊 / 开放性问题     → fusion
  - 语义扩展 / 专业领域   → hyde
  - auto 以外强制指定     → 直接路由
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.llm import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 策略 → (显示名, 一句话说明)
STRATEGY_META = {
    "baseline": ("Baseline RAG",  "标准向量检索，速度最快，适合精确事实查询"),
    "hyde":     ("HyDE RAG",      "生成假设文档后检索，适合专业/语义扩展查询"),
    "fusion":   ("RAG Fusion",    "多查询扩展+RRF融合，适合开放/模糊问题"),
    "crag":     ("CRAG",          "带相关性评估的纠正式RAG，适合不确定性高的场景"),
    "graph":    ("GraphRAG",      "知识图谱+向量融合，适合多实体关系/多跳推理"),
}

_ROUTER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一个 RAG 策略路由器。根据用户问题的特征，从以下策略中选出最合适的一个，只输出策略名称（小写英文单词），不要解释。

策略列表:
- baseline: 精确事实查询、定义、单跳问题
- hyde: 需要语义扩展的专业领域问题
- fusion: 模糊、开放性、需要多角度探索的问题
- crag: 答案不确定、需要验证可信度的问题
- graph: 涉及多个实体关系、需要多跳推理的复杂问题"""),
    ("human", "{question}"),
])


def route(question: str, strategy: str = "auto") -> str:
    """返回策略名称 (baseline | hyde | fusion | crag | graph)"""
    if strategy != "auto":
        return strategy

    try:
        llm = get_llm()
        raw = (_ROUTER_PROMPT | llm | StrOutputParser()).invoke({"question": question})
        chosen = raw.strip().lower().split()[0]
        if chosen in STRATEGY_META:
            return chosen
    except Exception:
        pass
    return "baseline"   # 降级


def dispatch(question: str, strategy: str = "auto") -> dict:
    """路由并执行对应策略，返回统一结构的结果"""
    from strategies import baseline_rag, hyde_rag, fusion_rag, crag, graph_rag

    chosen = route(question, strategy)
    runners = {
        "baseline": baseline_rag.run,
        "hyde":     hyde_rag.run,
        "fusion":   fusion_rag.run,
        "crag":     crag.run,
        "graph":    graph_rag.run,
    }
    result = runners[chosen](question=question)
    result["routed_strategy"] = chosen
    result["strategy_name"] = STRATEGY_META[chosen][0]
    result["strategy_desc"] = STRATEGY_META[chosen][1]
    return result
