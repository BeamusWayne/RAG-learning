"""
RAGAS evaluate() 综合评估 Demo
================================
使用 ragas.evaluate() 对多个样本同时运行全部 4 个指标，
输出综合评估结果表格。

评估流程：
1. 构建包含多个样本的 EvaluationDataset
2. 定义 4 个评估指标（Faithfulness, Answer Relevancy, Context Precision, Context Recall）
3. 调用 evaluate() 一次性批量评估
4. 输出 pandas DataFrame 格式的结果表格

运行: cd Projects/RAGAS-Learning && uv run python demos/demo_evaluate.py
"""

import os
import sys

from dotenv import load_dotenv
from langchain_community.embeddings import OpenAIEmbeddings as LCOpenAIEmbeddings
from openai import OpenAI
from ragas import evaluate
from ragas.dataset_schema import EvaluationDataset, SingleTurnSample
from ragas.llms import llm_factory
from ragas.metrics._answer_relevance import ResponseRelevancy
from ragas.metrics._context_precision import ContextPrecision
from ragas.metrics._context_recall import ContextRecall
from ragas.metrics._faithfulness import Faithfulness
from ragas.embeddings import LangchainEmbeddingsWrapper

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

ZHIPU_API_KEY = os.environ.get("ZHIPU_API_KEY", "")
ZHIPU_BASE_URL = os.environ.get("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")

if not ZHIPU_API_KEY:
    print("错误: 未找到 ZHIPU_API_KEY")
    sys.exit(1)


def main():
    print("RAGAS evaluate() 综合评估 Demo")
    print("=" * 60)

    client = OpenAI(api_key=ZHIPU_API_KEY, base_url=ZHIPU_BASE_URL)
    llm = llm_factory("glm-4-plus", client=client)

    embeddings = LangchainEmbeddingsWrapper(
        embeddings=LCOpenAIEmbeddings(
            model="embedding-3",
            openai_api_key=ZHIPU_API_KEY,
            openai_api_base=ZHIPU_BASE_URL,
        )
    )

    metrics = [
        Faithfulness(llm=llm),
        ResponseRelevancy(llm=llm, embeddings=embeddings, strictness=1),
        ContextPrecision(llm=llm),
        ContextRecall(llm=llm),
    ]

    samples = [
        SingleTurnSample(
            user_input="爱因斯坦有哪些重要贡献？",
            response=(
                "爱因斯坦提出了狭义相对论和广义相对论，"
                "并因光电效应定律获得了诺贝尔物理学奖。"
            ),
            reference=(
                "爱因斯坦提出了狭义相对论和广义相对论，"
                "并因光电效应定律获得了诺贝尔物理学奖。"
            ),
            retrieved_contexts=[
                "爱因斯坦于 1905 年提出狭义相对论，1915 年提出广义相对论。",
                "爱因斯坦因发现光电效应定律获得 1921 年诺贝尔物理学奖。",
            ],
        ),
        SingleTurnSample(
            user_input="量子力学的基本原理是什么？",
            response=(
                "量子力学的基本原理包括波粒二象性、不确定性原理和量子叠加态。"
                "薛定谔方程是量子力学的核心方程。"
            ),
            reference=(
                "量子力学的核心原理包括波粒二象性、海森堡不确定性原理、"
                "量子叠加和量子纠缠。薛定谔方程描述了量子态的演化。"
            ),
            retrieved_contexts=[
                "波粒二象性是量子力学的基本概念，微观粒子同时具有波动和粒子特性。",
                "海森堡不确定性原理指出无法同时精确测量粒子的位置和动量。",
                "薛定谔方程是量子力学中描述量子态随时间演化的基本方程。",
            ],
        ),
        SingleTurnSample(
            user_input="光合作用的步骤是什么？",
            response=(
                "光合作用分为光反应和暗反应两个阶段。"
                "光反应在叶绿体的类囊体膜上进行，产生 ATP 和 NADPH。"
            ),
            reference=(
                "光合作用包括光反应和暗反应（Calvin 循环）。"
                "光反应将光能转化为化学能（ATP 和 NADPH），"
                "暗反应利用这些能量将 CO2 固定为有机物。"
            ),
            retrieved_contexts=[
                "光反应发生在叶绿体类囊体膜上，水分子被光解产生氧气、ATP 和 NADPH。",
            ],
        ),
    ]

    dataset = EvaluationDataset(samples=samples)

    print(f"评估样本数: {len(samples)}")
    print(f"评估指标: {[m.__class__.__name__ for m in metrics]}")
    print("\n开始批量评估（可能需要 1-2 分钟）...\n")

    result = evaluate(
        dataset=dataset,
        metrics=metrics,
        llm=llm,
        embeddings=embeddings,
        show_progress=True,
    )

    df = result.to_pandas()
    print("\n" + "=" * 60)
    print("综合评估结果")
    print("=" * 60)
    print(df.to_string(index=False))

    metric_cols = [c for c in df.columns if c not in ("user_input", "response", "reference", "retrieved_contexts")]
    print("\n" + "=" * 60)
    print("各指标平均分")
    print("=" * 60)
    for col in metric_cols:
        print(f"  {col}: {df[col].mean():.4f}")


if __name__ == "__main__":
    main()
