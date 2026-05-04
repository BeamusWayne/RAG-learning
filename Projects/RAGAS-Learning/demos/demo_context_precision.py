"""
RAGAS Context Precision（上下文精度）学习 Demo
================================================
Context Precision 衡量检索到的上下文中，相关内容是否排名靠前。
好的检索系统应该把最相关的片段排在前面。

评估流程：
1. 对每个检索上下文，判断它是否与回答问题相关
2. 根据相关上下文的排名位置计算加权分数
3. 相关内容排在越前面 → 分数越高

运行: cd Projects/RAGAS-Learning && python demos/demo_context_precision.py
"""

import asyncio
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI
from ragas.dataset_schema import SingleTurnSample
from ragas.llms import llm_factory
from ragas.metrics._context_precision import ContextPrecision

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

ZHIPU_API_KEY = os.environ.get("ZHIPU_API_KEY", "")
ZHIPU_BASE_URL = os.environ.get("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")

if not ZHIPU_API_KEY:
    print("错误: 未找到 ZHIPU_API_KEY")
    sys.exit(1)


async def evaluate_context_precision(
    user_input: str,
    reference: str,
    retrieved_contexts: list[str],
    label: str,
    llm,
) -> float:
    scorer = ContextPrecision(llm=llm)
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
    for i, ctx in enumerate(retrieved_contexts):
        print(f"  上下文[{i}]: {ctx[:50]}...")
    print(f"精度: {score:.4f}")
    return score


async def main():
    print("RAGAS Context Precision（上下文精度）评估 Demo")
    print("=" * 60)

    client = OpenAI(api_key=ZHIPU_API_KEY, base_url=ZHIPU_BASE_URL)
    llm = llm_factory("glm-4-plus", client=client)

    # 用例 1: 高精度 — 相关上下文排在前面
    score_high = await evaluate_context_precision(
        user_input="相对论是谁提出的？",
        reference="相对论由阿尔伯特·爱因斯坦提出，包括狭义相对论和广义相对论。",
        retrieved_contexts=[
            "阿尔伯特·爱因斯坦于 1905 年提出狭义相对论，1915 年提出广义相对论。",
            "牛顿的经典力学在高速运动情况下不再适用。",
            "量子力学是研究微观粒子行为的物理学分支。",
        ],
        label="高精度（相关上下文排第一）",
        llm=llm,
    )

    # 用例 2: 低精度 — 相关上下文排在后面
    score_low = await evaluate_context_precision(
        user_input="相对论是谁提出的？",
        reference="相对论由阿尔伯特·爱因斯坦提出，包括狭义相对论和广义相对论。",
        retrieved_contexts=[
            "量子力学是研究微观粒子行为的物理学分支。",
            "牛顿的经典力学在高速运动情况下不再适用。",
            "阿尔伯特·爱因斯坦于 1905 年提出狭义相对论，1915 年提出广义相对论。",
        ],
        label="低精度（相关上下文排最后）",
        llm=llm,
    )

    print(f"\n{'='*60}")
    print("评估结果汇总")
    print(f"{'='*60}")
    print(f"高精度（相关排第一）: {score_high:.4f}")
    print(f"低精度（相关排最后）: {score_low:.4f}")
    if score_high > score_low:
        print("\n验证通过: 相关上下文排前面的用例得分更高")
    else:
        print("\n警告: 分数关系不符合预期")


if __name__ == "__main__":
    asyncio.run(main())
