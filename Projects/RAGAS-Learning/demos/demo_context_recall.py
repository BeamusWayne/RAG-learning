"""
RAGAS Context Recall（上下文召回）学习 Demo
=============================================
Context Recall 衡量标准答案中的信息是否都被检索到的上下文覆盖。
遗漏关键信息 → 低召回。

评估流程：
1. 将 reference（标准答案）拆分为多个关键陈述
2. 判断每个陈述是否能从 retrieved_contexts 中找到支持
3. 被覆盖的陈述占比 → Context Recall 分数

运行: cd Projects/RAGAS-Learning && python demos/demo_context_recall.py
"""

import asyncio
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI
from ragas.dataset_schema import SingleTurnSample
from ragas.llms import llm_factory
from ragas.metrics._context_recall import ContextRecall

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

ZHIPU_API_KEY = os.environ.get("ZHIPU_API_KEY", "")
ZHIPU_BASE_URL = os.environ.get("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")

if not ZHIPU_API_KEY:
    print("错误: 未找到 ZHIPU_API_KEY")
    sys.exit(1)


async def evaluate_context_recall(
    user_input: str,
    reference: str,
    retrieved_contexts: list[str],
    label: str,
    llm,
) -> float:
    scorer = ContextRecall(llm=llm)
    sample = SingleTurnSample(
        user_input=user_input,
        reference=reference,
        retrieved_contexts=retrieved_contexts,
    )
    score = await scorer.single_turn_ascore(sample)
    print(f"\n{'='*60}")
    print(f"用例: {label}")
    print(f"{'='*60}")
    print(f"问题: {user_input}")
    print(f"标准答案: {reference[:60]}...")
    for i, ctx in enumerate(retrieved_contexts):
        print(f"  上下文[{i}]: {ctx[:50]}...")
    print(f"召回率: {score:.4f}")
    return score


async def main():
    print("RAGAS Context Recall（上下文召回）评估 Demo")
    print("=" * 60)

    client = OpenAI(api_key=ZHIPU_API_KEY, base_url=ZHIPU_BASE_URL)
    llm = llm_factory("glm-4-plus", client=client)

    # 用例 1: 高召回 — 上下文覆盖了标准答案的全部信息
    score_high = await evaluate_context_recall(
        user_input="爱因斯坦有哪些重要贡献？",
        reference=(
            "爱因斯坦提出了狭义相对论和广义相对论，"
            "并因光电效应定律获得了诺贝尔物理学奖。"
        ),
        retrieved_contexts=[
            "爱因斯坦于 1905 年提出狭义相对论，1915 年提出广义相对论。",
            "爱因斯坦因发现光电效应定律获得 1921 年诺贝尔物理学奖。",
        ],
        label="高召回（上下文覆盖全部信息）",
        llm=llm,
    )

    # 用例 2: 低召回 — 上下文遗漏了诺贝尔奖信息
    score_low = await evaluate_context_recall(
        user_input="爱因斯坦有哪些重要贡献？",
        reference=(
            "爱因斯坦提出了狭义相对论和广义相对论，"
            "并因光电效应定律获得了诺贝尔物理学奖。"
        ),
        retrieved_contexts=[
            "爱因斯坦于 1905 年提出狭义相对论，1915 年提出广义相对论。",
        ],
        label="低召回（遗漏诺贝尔奖信息）",
        llm=llm,
    )

    print(f"\n{'='*60}")
    print("评估结果汇总")
    print(f"{'='*60}")
    print(f"高召回（完整覆盖）: {score_high:.4f}")
    print(f"低召回（信息遗漏）: {score_low:.4f}")
    if score_high > score_low:
        print("\n验证通过: 完整召回的用例得分更高")
    else:
        print("\n警告: 分数关系不符合预期")


if __name__ == "__main__":
    asyncio.run(main())
