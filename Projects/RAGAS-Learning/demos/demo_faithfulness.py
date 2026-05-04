"""
RAGAS Faithfulness（忠实度）学习 Demo
======================================
Faithfulness 衡量答案中的每个声明是否都能在检索上下文中找到依据。
高分 = 答案忠实于上下文，低分 = 存在幻觉（编造的信息）。

评估流程：
1. 从 response 中提取所有声明（claims）
2. 逐条判断每条声明是否被 retrieved_contexts 支持
3. 计算支持的声明占比 → Faithfulness 分数

运行: cd Projects/RAGAS-Learning && python demos/demo_faithfulness.py
"""

import asyncio
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI
from ragas.dataset_schema import SingleTurnSample
from ragas.llms import llm_factory
from ragas.metrics._faithfulness import Faithfulness

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

if not os.environ.get("OPENAI_API_KEY"):
    print("错误: 未找到 OPENAI_API_KEY，请在仓库根目录 .env 中设置")
    sys.exit(1)


async def evaluate_faithfulness(
    user_input: str,
    response: str,
    retrieved_contexts: list[str],
    label: str,
    llm,
) -> float:
    scorer = Faithfulness(llm=llm)
    sample = SingleTurnSample(
        user_input=user_input,
        response=response,
        retrieved_contexts=retrieved_contexts,
    )
    score = await scorer.single_turn_ascore(sample)
    print(f"\n{'='*60}")
    print(f"用例: {label}")
    print(f"{'='*60}")
    print(f"问题:     {user_input}")
    print(f"答案:     {response}")
    print(f"上下文:   {retrieved_contexts[0][:80]}...")
    print(f"忠实度:   {score:.4f}")
    return score


async def main():
    print("RAGAS Faithfulness（忠实度）评估 Demo")
    print("=" * 60)

    llm = llm_factory("gpt-4o-mini", client=OpenAI())

    # 用例 1: 高忠实度 — 答案完全基于上下文
    score_high = await evaluate_faithfulness(
        user_input="爱因斯坦最著名的理论是什么？",
        response=(
            "爱因斯坦最著名的理论是相对论。"
            "他于 1905 年发表了狭义相对论，于 1915 年发表了广义相对论。"
        ),
        retrieved_contexts=[
            "阿尔伯特·爱因斯坦（Albert Einstein）是著名的理论物理学家。"
            "他于 1905 年发表了狭义相对论，这一理论彻底改变了人们对时间和空间的理解。"
            "1915 年，他又发表了广义相对论，将引力解释为时空弯曲。"
            "他因发现光电效应定律获得 1921 年诺贝尔物理学奖。"
        ],
        label="高忠实度（答案基于上下文）",
        llm=llm,
    )

    # 用例 2: 低忠实度（幻觉）— 编造了上下文里不存在的信息
    score_low = await evaluate_faithfulness(
        user_input="爱因斯坦最著名的理论是什么？",
        response=(
            "爱因斯坦最著名的理论是量子力学。"
            "他于 1899 年在柏林大学提出了这一理论，"
            "并因此获得了诺贝尔化学奖。"
        ),
        retrieved_contexts=[
            "阿尔伯特·爱因斯坦（Albert Einstein）是著名的理论物理学家。"
            "他于 1905 年发表了狭义相对论，这一理论彻底改变了人们对时间和空间的理解。"
            "1915 年，他又发表了广义相对论，将引力解释为时空弯曲。"
            "他因发现光电效应定律获得 1921 年诺贝尔物理学奖。"
        ],
        label="低忠实度（包含幻觉）",
        llm=llm,
    )

    print(f"\n{'='*60}")
    print("评估结果汇总")
    print(f"{'='*60}")
    print(f"高忠实度用例: {score_high:.4f}")
    print(f"低忠实度用例: {score_low:.4f}")
    if score_high > score_low:
        print("\n验证通过: 高忠实度得分 > 低忠实度得分")
    else:
        print("\n警告: 分数关系不符合预期，请检查 LLM 输出")


if __name__ == "__main__":
    asyncio.run(main())
