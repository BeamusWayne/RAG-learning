# -*- coding: utf-8 -*-
"""
场景一：玩家智能问答助手 - 工具函数模板
供 RAG 无匹配时调用，可绑定为 LangChain/LangGraph 的 tool。
返回结构统一为 dict，便于 Agent 解析与回复。
"""

from typing import Any


# 模拟道具数据：道具名 -> 描述、获取方式等
_ITEMS_DB = {
    "传说之剑": {
        "name": "传说之剑",
        "desc": "上古流传的神兵，攻击+320，暴击率+15%",
        "obtain": "深渊副本第10层首通 / 活动商店兑换",
        "effect": "普攻有概率触发剑气，对直线敌人造成额外伤害",
    },
    "回血药水": {
        "name": "回血药水",
        "desc": "恢复生命值，分初/中/高三级",
        "obtain": "主城杂货店、副本商人、商城消耗品",
        "effect": "初级20%、中级40%、高级60%生命恢复，共用30秒冷却",
    },
    "体力药水": {
        "name": "体力药水",
        "desc": "使用后立即恢复50点体力",
        "obtain": "每日任务、活动奖励、商城购买",
        "effect": "恢复50体力，每日使用上限5瓶",
    },
    "技能书": {
        "name": "技能书",
        "desc": "用于学习或升级技能",
        "obtain": "任务奖励、副本掉落、竞技场段位奖励",
        "effect": "使用后解锁或提升对应技能等级",
    },
}


# 模拟活动/技能数据：关键词 -> 说明
_EVENTS_SKILLS_DB = {
    "春节活动": {
        "type": "活动",
        "name": "春节活动",
        "time": "1月28日 - 2月10日",
        "content": "限定副本、兑换商店、登录送红包",
    },
    "周末双倍": {
        "type": "活动",
        "name": "周末双倍",
        "time": "每周六、日全天",
        "content": "经验与金币副本双倍奖励",
    },
    "火焰斩": {
        "type": "技能",
        "name": "火焰斩",
        "cooldown": "8秒（满级6秒）",
        "content": "向前方挥出火焰剑气，造成范围伤害",
    },
    "冰冻术": {
        "type": "技能",
        "name": "冰冻术",
        "cooldown": "12秒",
        "content": "控制持续2秒，受韧性影响",
    },
}


def query_item(item_name: str) -> dict[str, Any]:
    """
    根据道具名称查询道具描述与获取方式。
    用于 RAG 无法回答的道具类问题时由 Agent 调用。

    :param item_name: 道具名称，如「传说之剑」「回血药水」
    :return: {"found": bool, "data": {...} 或 None, "message": str}
    """
    item_name = (item_name or "").strip()
    if not item_name:
        return {"found": False, "data": None, "message": "请提供道具名称"}
    for key, val in _ITEMS_DB.items():
        if key in item_name or item_name in key:
            return {"found": True, "data": val, "message": "查询成功"}
    return {"found": False, "data": None, "message": f"未找到道具「{item_name}」的相关信息"}


def query_event_or_skill(keyword: str) -> dict[str, Any]:
    """
    根据关键词查询活动或技能说明（时间、效果等）。
    用于 RAG 无法回答的活动/技能类问题时由 Agent 调用。

    :param keyword: 关键词，如「春节活动」「火焰斩」
    :return: {"found": bool, "data": {...} 或 None, "message": str}
    """
    keyword = (keyword or "").strip()
    if not keyword:
        return {"found": False, "data": None, "message": "请提供活动或技能名称"}
    for key, val in _EVENTS_SKILLS_DB.items():
        if key in keyword or keyword in key:
            return {"found": True, "data": val, "message": "查询成功"}
    return {"found": False, "data": None, "message": f"未找到「{keyword}」的相关信息"}
