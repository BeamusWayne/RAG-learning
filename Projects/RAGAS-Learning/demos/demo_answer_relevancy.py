"""
RAGAS Answer Relevancy（答案相关性）学习 Demo
===============================================
Answer Relevancy 衡量生成的答案与用户提问的相关程度。
高分 = 答案切题，低分 = 答非所问。

评估流程：
1. 从 response 反向生成可能的问题
2. 计算生成问题与原始问题的语义相似度
3. 相似度越高 → 答案越切题

运行: cd Projects/RAGAS-Learning && python demos/demo_answer_relevancy.py
"""

import asyncio
import os
import sys

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
from ragas.dataset_schema import SingleTurnSample
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import llm_factory
from ragas.metrics._answer_relevance import ResponseRelevancy

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

ZHIPU_API_KEY = os.environ.get("ZHIPU_API_KEY", "")
ZHIPU_BASE_URL = os.environ.get("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
ZHIPU_CHAT_MODEL = os.environ.get("ZHIPU_CHAT_MODEL", "glm-4-flash")

if not ZHIPU_API_KEY:
    print("错误: 未找到 ZHIPU_API_KEY，请在仓库根目录 .env 中设置")
    sys.exit(1)


async def evaluate_relevancy(
    user_input: str,
    response: str,
    label: str,
    llm,
    embeddings,
) -> float:
    scorer = ResponseRelevancy(llm=llm, embeddings=embeddings, strictness=1)
    sample = SingleTurnSample(
        user_input=user_input,
        response=response,
    )
    score = await scorer.single_turn_ascore(sample)
    print(f"\n{'='*60}")
    print(f"用例: {label}")
    print(f"{'='*60}")
    print(f"问题: {user_input}")
    print(f"答案: {response[:60]}{'...' if len(response) > 60 else ''}")
    print(f"相关性: {score:.4f}")
    return score


async def main():
    print("RAGAS Answer Relevancy（答案相关性）评估 Demo")
    print("=" * 60)
    print(f"使用模型: {ZHIPU_CHAT_MODEL} ({ZHIPU_BASE_URL})")

    client = OpenAI(api_key=ZHIPU_API_KEY, base_url=ZHIPU_BASE_URL)
    llm = llm_factory("glm-4-plus", client=client)

    emb_client = OpenAIEmbeddings(
        model="embedding-3",
        api_key=ZHIPU_API_KEY,
        base_url=ZHIPU_BASE_URL,
    )
    embeddings = LangchainEmbeddingsWrapper(embeddings=emb_client)

    # 用例 1: 相关答案
    score_high = await evaluate_relevancy(
        user_input="Python 的列表推导式是什么？",
        response=(
            "列表推导式是 Python 中从已有列表创建新列表的简洁语法。"
            "例如 [x**2 for x in range(5)] 会生成 [0, 1, 4, 9, 16]。"
            "它比传统的 for 循环更简洁、执行更快。"
        ),
        label="相关答案（切题）",
        llm=llm,
        embeddings=embeddings,
    )

    # 用例 2: 不相关答案
    score_low = await evaluate_relevancy(
        user_input="Python 的列表推导式是什么？",
        response=(
            "Java 是一种面向对象的编程语言，由 Sun Microsystems 于 1995 年发布。"
            "它广泛用于企业级应用开发。Java 的垃圾回收机制可以自动管理内存。"
        ),
        label="不相关答案（答非所问）",
        llm=llm,
        embeddings=embeddings,
    )

    print(f"\n{'='*60}")
    print("评估结果汇总")
    print(f"{'='*60}")
    print(f"相关答案:   {score_high:.4f}")
    print(f"不相关答案: {score_low:.4f}")
    if score_high > score_low:
        print("\n验证通过: 相关答案得分 > 不相关答案")
    else:
        print("\n警告: 分数关系不符合预期，请检查 LLM 输出")


if __name__ == "__main__":
    asyncio.run(main())
