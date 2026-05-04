"""
RAGAS 合成测试数据集生成 Demo
================================
使用 TestsetGenerator 从文档自动生成 question-answer-contexts 测试集。
省去手工标注的痛苦。

核心流程：
1. 准备文档（LangChain Document 格式）
2. 配置 LLM + Embeddings
3. TestsetGenerator.generate_with_langchain_docs() 生成测试集
4. 输出 question, answer, contexts 字段

运行: cd Projects/RAGAS-Learning && uv run python demos/demo_testset_generator.py
"""

import os
import sys

from dotenv import load_dotenv
from langchain_community.embeddings import OpenAIEmbeddings as LCOpenAIEmbeddings
from langchain_core.documents import Document
from openai import OpenAI
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import llm_factory
from ragas.testset import TestsetGenerator

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

ZHIPU_API_KEY = os.environ.get("ZHIPU_API_KEY", "")
ZHIPU_BASE_URL = os.environ.get("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")

if not ZHIPU_API_KEY:
    print("错误: 未找到 ZHIPU_API_KEY")
    sys.exit(1)


def main():
    print("RAGAS 合成测试数据集生成 Demo")
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

    docs = [
        Document(
            page_content=(
                "相对论是阿尔伯特·爱因斯坦提出的物理学理论，分为狭义相对论和广义相对论。"
                "狭义相对论于1905年提出，揭示了时间和空间的相对性，以及质能等价关系（E=mc²）。"
                "广义相对论于1915年提出，将引力解释为时空弯曲的几何效应。"
                "爱因斯坦因发现光电效应定律获得1921年诺贝尔物理学奖。"
            ),
            metadata={"source": "physics_relativity"},
        ),
        Document(
            page_content=(
                "量子力学是研究微观粒子行为的物理学分支。"
                "核心概念包括波粒二象性（粒子同时具有波动和粒子特性）、"
                "海森堡不确定性原理（无法同时精确测量位置和动量）、"
                "量子叠加（粒子可同时处于多个状态）和量子纠缠（粒子间的非局域关联）。"
                "薛定谔方程描述了量子态随时间的演化。"
            ),
            metadata={"source": "physics_quantum"},
        ),
        Document(
            page_content=(
                "光合作用是绿色植物利用光能将二氧化碳和水转化为有机物和氧气的生化过程。"
                "分为两个阶段：光反应发生在叶绿体类囊体膜上，水被光解产生氧气、ATP和NADPH；"
                "暗反应（Calvin循环）在叶绿体基质中进行，利用ATP和NADPH将CO2固定为有机物。"
                "光合作用是地球上几乎所有生态系统的能量来源。"
            ),
            metadata={"source": "biology_photosynthesis"},
        ),
        Document(
            page_content=(
                "深度学习是机器学习的一个子领域，使用多层神经网络来学习数据的层次化表示。"
                "卷积神经网络（CNN）擅长图像识别，循环神经网络（RNN）适合序列数据处理。"
                "Transformer架构基于自注意力机制，是GPT、BERT等大语言模型的基础。"
                "2012年AlexNet在ImageNet竞赛中的突破性表现标志着深度学习时代的到来。"
            ),
            metadata={"source": "ai_deep_learning"},
        ),
    ]

    print(f"文档数: {len(docs)}")
    print(f"文档主题: {[d.metadata['source'] for d in docs]}")
    print("\n开始生成测试数据集（可能需要 2-3 分钟）...\n")

    generator = TestsetGenerator(llm=llm, embedding_model=embeddings)

    testset = generator.generate_with_langchain_docs(
        docs,
        testset_size=5,
    )

    df = testset.to_pandas()

    print("\n" + "=" * 60)
    print("生成的测试数据集")
    print("=" * 60)

    for i, row in df.iterrows():
        print(f"\n--- 样本 {i + 1} ---")
        print(f"问题: {row['user_input']}")
        print(f"参考答案: {str(row.get('reference', ''))[:100]}...")
        contexts = row.get("retrieved_contexts", [])
        if isinstance(contexts, list):
            for j, ctx in enumerate(contexts[:2]):
                print(f"  上下文[{j}]: {str(ctx)[:80]}...")
        print()

    print("=" * 60)
    print(f"生成样本数: {len(df)}")
    print(f"列名: {list(df.columns)}")
    print("=" * 60)

    if len(df) >= 3:
        print("\n验证通过: 成功生成至少 3 条测试样本")
    else:
        print("\n警告: 生成样本数不足 3 条")


if __name__ == "__main__":
    main()
