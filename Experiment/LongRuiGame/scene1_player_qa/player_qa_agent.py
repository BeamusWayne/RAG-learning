# -*- coding: utf-8 -*-
"""
基于 LangChain 的游戏玩家智能问答助手 Agent。
流程：先判模糊问句→反问澄清；再匹配 RAG 语料（game_faq.json）；无匹配时再调用工具。
用户问题与助手回答会记录到本目录下的 qa_log.jsonl。
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool

# 项目根：LongRuiGame
_LONG_RUI_ROOT = Path(__file__).resolve().parent.parent
_SCENE_DIR = Path(__file__).resolve().parent
if str(_LONG_RUI_ROOT) not in sys.path:
    sys.path.insert(0, str(_LONG_RUI_ROOT))

from tool_templates import query_event_or_skill, query_item

# 日志文件：存放在 scene1_player_qa 下，每行一条 JSON（时间戳、用户问、助手答、来源）
QA_LOG_PATH = _SCENE_DIR / "qa_log.jsonl"
FAQ_PATH = _LONG_RUI_ROOT / "game_faq.json"
RAG_THRESHOLD = 0.35

# 模糊指代词：问句中出现且未带明确实体名时，先反问澄清（如「那个剑怎么得」→「您是指传说之剑吗？」）
VAGUE_MARKERS = ("那个", "这个", "某", "哪种", "啥", "哪个", "哪把", "啥活动", "哪个活动", "什么剑", "什么活动")
# 已知实体名：问句中出现则视为已指名，不触发反问
KNOWN_ENTITY_NAMES = (
    "传说之剑", "回血药水", "体力药水", "技能书", "火焰斩", "冰冻术",
    "春节活动", "周末双倍", "世界Boss", "竞技场", "签到", "每日任务", "副本", "组队", "公会", "钻石", "金币",
)


def _is_vague_query(query: str) -> bool:
    """判断是否为模糊问句（含指代但未写出具体道具/活动/技能名），此类应先反问。"""
    q = (query or "").strip()
    if not q:
        return False
    has_vague = any(m in q for m in VAGUE_MARKERS)
    has_entity = any(e in q for e in KNOWN_ENTITY_NAMES)
    return bool(has_vague and not has_entity)


def _get_llm():
    """优先通义/OpenAI，无则 Ollama。"""
    api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            from langchain_openai import ChatOpenAI
            base = os.getenv("OPENAI_API_BASE") or "https://dashscope.aliyuncs.com/compatible-mode/v1"
            if "dashscope" in base:
                return ChatOpenAI(model="qwen-max", base_url=base, api_key=api_key)
            return ChatOpenAI(model="qwen3-max", api_key=api_key)
        except Exception:
            pass
    from langchain_ollama import ChatOllama
    return ChatOllama(model="qwen3-vl:4b", base_url="http://localhost:11434", temperature=0.2)


def _jaccard_sim(s1: str, s2: str) -> float:
    s1, s2 = (s1 or "").strip(), (s2 or "").strip()
    if not s1 or not s2:
        return 0.0
    a, b = set(s1), set(s2)
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def _load_faq() -> list[dict[str, Any]]:
    if not FAQ_PATH.exists():
        return []
    with open(FAQ_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def rag_match(query: str) -> tuple[bool, str | None]:
    """先匹配 RAG 语料，命中返回 (True, answer)，否则 (False, None)。"""
    faq_list = _load_faq()
    if not faq_list:
        return False, None
    query = (query or "").strip()
    if not query:
        return False, None
    best_score, best_answer = 0.0, None
    for item in faq_list:
        q, a = item.get("q", ""), item.get("a", "")
        if not q or not a:
            continue
        if q in query or query in q:
            return True, a
        score = _jaccard_sim(query, q)
        if score > best_score:
            best_score, best_answer = score, a
    if best_score >= RAG_THRESHOLD and best_answer:
        return True, best_answer
    return False, None


def _log_qa(query: str, answer: str, source: str) -> None:
    """将本条问答追加到 scene1_player_qa/qa_log.jsonl。"""
    import time
    record = {
        "ts": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "query": query,
        "answer": answer,
        "source": source,
    }
    QA_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(QA_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# 工具：供 LangChain 在 RAG 无匹配时调用
@tool
def query_item_tool(item_name: str) -> str:
    """查询道具的获取方式与效果。参数：道具名称，如传说之剑、回血药水。"""
    out = query_item(item_name)
    if out.get("found") and out.get("data"):
        d = out["data"]
        return f"【{d.get('name','')}】{d.get('desc','')}；获取：{d.get('obtain','')}；效果：{d.get('effect','')}"
    return out.get("message", "未找到该道具信息")


@tool
def query_event_or_skill_tool(keyword: str) -> str:
    """查询活动时间或技能说明。参数：活动或技能名称，如春节活动、火焰斩。"""
    out = query_event_or_skill(keyword)
    if out.get("found") and out.get("data"):
        d = out["data"]
        return f"【{d.get('name','')}】类型：{d.get('type','')}；时间/冷却：{d.get('time','') or d.get('cooldown','')}；说明：{d.get('content','')}"
    return out.get("message", "未找到相关信息")


TOOLS = [query_item_tool, query_event_or_skill_tool]
SYSTEM_PROMPT = """你是游戏客服小助手，用口语化、亲切的玩家口吻回答。当需要查道具/活动/技能时请调用对应工具，然后根据工具结果用一句话总结回复。"""

# 模糊问句反问提示：只生成一句澄清问句，不查 RAG、不调工具
CLARIFY_PROMPT = """玩家问的是：「{query}」
请用一句话反问澄清，让玩家确认具体指哪个道具/活动/技能。例如：您是指传说之剑吗？/ 您说的是哪个剑？/ 您问的是春节活动还是周末双倍？
只输出一句简短、友好的反问，不要直接给出答案。"""


def _answer_clarify(query: str) -> str:
    """模糊问句：用 LLM 生成一句反问澄清（如「您是指传说之剑吗？」），不查 RAG、不调工具。"""
    llm = _get_llm()
    prompt = CLARIFY_PROMPT.format(query=query)
    response = llm.invoke([HumanMessage(content=prompt)])
    return (response.content or "您能具体说是哪个道具或活动吗？").strip()


def _answer_with_tools(query: str) -> str:
    """RAG 无匹配时：LLM + 工具调用，返回最终回复（仅用 LangChain，无 LangGraph）。"""
    from langchain_core.messages import ToolMessage
    llm = _get_llm().bind_tools(TOOLS)
    messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=query)]
    response = llm.invoke(messages)
    if not response.tool_calls:
        return (response.content or "抱歉，暂时没有相关说明，您可以描述得更具体一些～").strip()
    tool_by_name = {t.name: t for t in TOOLS}
    tool_messages = []
    for tc in response.tool_calls:
        _id = tc.get("id", "") if isinstance(tc, dict) else getattr(tc, "id", "")
        name = tc.get("name", "") if isinstance(tc, dict) else getattr(tc, "name", "")
        args = tc.get("args", {}) if isinstance(tc, dict) else getattr(tc, "args", {})
        if name not in tool_by_name:
            tool_messages.append(ToolMessage(content="未知工具", tool_call_id=_id))
            continue
        result = tool_by_name[name].invoke(args)
        tool_messages.append(ToolMessage(content=str(result), tool_call_id=_id))
    all_messages = messages + [response] + tool_messages
    final = _get_llm().invoke(
        all_messages + [HumanMessage(content="请根据上述工具返回结果，用一句简短友好的玩家口吻总结回复。")]
    )
    return (final.content or "已为您查询，暂无更多信息。").strip()


def ask(query: str) -> str:
    """对外入口：先判模糊→反问；再 RAG；无匹配再调工具；结果写入 qa_log.jsonl。"""
    query = (query or "").strip()
    if not query:
        answer = "请说出您想了解的内容～"
        _log_qa(query or "(空)", answer, "rag")
        return answer
    # 模糊问句：先反问澄清（如「那个剑怎么得」→「您是指传说之剑吗？」）
    if _is_vague_query(query):
        answer = _answer_clarify(query)
        _log_qa(query, answer, "clarify")
        return answer
    matched, rag_answer = rag_match(query)
    if matched and rag_answer:
        _log_qa(query, rag_answer, "rag")
        return rag_answer
    answer = _answer_with_tools(query)
    _log_qa(query, answer, "tools")
    return answer


if __name__ == "__main__":
    q = input("玩家问：").strip() or "每日任务几点刷新"
    print("助手答：", ask(q))
    print("已写入日志：", QA_LOG_PATH)
