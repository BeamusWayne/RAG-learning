"""
RAGAS 对比评估 Demo: Naive RAG vs Reranked RAG
=================================================
对同一批问题分别用 naive retrieval 和 reranked retrieval 生成答案，
用 RAGAS 评估两者差异并输出对比表格。

核心流程：
1. 构建小型知识库（文档 → chunks → embeddings）
2. Naive RAG: 直接用向量相似度 top-k 检索
3. Reranked RAG: 先多召回候选，再用 LLM 打分重排序
4. 用 LLM 基于检索上下文生成答案
5. RAGAS evaluate() 对比两种策略的 4 维指标

运行: cd Projects/RAGAS-Learning && uv run python demos/demo_rag_comparison.py
"""

import os
import sys

import numpy as np
from dotenv import load_dotenv
from langchain_community.embeddings import OpenAIEmbeddings as LCOpenAIEmbeddings
from openai import OpenAI
from ragas import evaluate
from ragas.dataset_schema import EvaluationDataset, SingleTurnSample
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import llm_factory
from ragas.metrics._answer_relevance import ResponseRelevancy
from ragas.metrics._context_precision import ContextPrecision
from ragas.metrics._context_recall import ContextRecall
from ragas.metrics._faithfulness import Faithfulness

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

ZHIPU_API_KEY = os.environ.get("ZHIPU_API_KEY", "")
ZHIPU_BASE_URL = os.environ.get("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")

if not ZHIPU_API_KEY:
    print("错误: 未找到 ZHIPU_API_KEY")
    sys.exit(1)

KNOWLEDGE_BASE = [
    "阿尔伯特·爱因斯坦于1905年提出狭义相对论，揭示了时间和空间的相对性以及质能等价关系 E=mc²。",
    "爱因斯坦于1915年提出广义相对论，将引力解释为时空弯曲的几何效应。",
    "爱因斯坦因发现光电效应定律获得1921年诺贝尔物理学奖，光电效应是光子将能量传递给电子的现象。",
    "量子力学是研究微观粒子行为的物理学分支，由普朗克、玻尔、海森堡、薛定谔等人共同奠基。",
    "海森堡不确定性原理指出无法同时精确测量粒子的位置和动量，这是量子力学的基本特征。",
    "薛定谔方程是量子力学的核心方程，描述了量子态随时间的演化。",
    "光合作用分为光反应和暗反应两个阶段。光反应发生在类囊体膜上，产生ATP和NADPH。",
    "暗反应也称Calvin循环，在叶绿体基质中进行，利用ATP和NADPH将CO2固定为有机物。",
    "Transformer架构由Vaswani等人在2017年提出，基于自注意力机制，是GPT和BERT的基础。",
    "卷积神经网络（CNN）通过卷积层提取图像的局部特征，广泛用于图像识别和计算机视觉。",
]

QUESTIONS = [
    {
        "question": "爱因斯坦有哪些重要贡献？",
        "reference": (
            "爱因斯坦提出了狭义相对论和广义相对论，"
            "并因光电效应定律获得了诺贝尔物理学奖。"
        ),
    },
    {
        "question": "光合作用的两个阶段分别是什么？",
        "reference": (
            "光合作用分为光反应和暗反应。"
            "光反应在类囊体膜上产生ATP和NADPH，"
            "暗反应（Calvin循环）利用它们将CO2固定为有机物。"
        ),
    },
    {
        "question": "Transformer架构有什么特点？",
        "reference": (
            "Transformer由Vaswani等人在2017年提出，"
            "基于自注意力机制，是GPT和BERT等大语言模型的基础。"
        ),
    },
]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    a_arr = np.array(a)
    b_arr = np.array(b)
    return float(np.dot(a_arr, b_arr) / (np.linalg.norm(a_arr) * np.linalg.norm(b_arr) + 1e-8))


def naive_retrieve(query_embedding: list[float], doc_embeddings: list[list[float]], top_k: int = 2) -> list[int]:
    scores = [cosine_similarity(query_embedding, de) for de in doc_embeddings]
    ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    return ranked[:top_k]


def rerank_with_llm(
    client: OpenAI,
    query: str,
    chunks: list[str],
    candidate_indices: list[int],
    top_k: int = 2,
) -> list[int]:
    numbered = "\n".join(f"段落{i}: {chunks[i]}" for i in candidate_indices)
    prompt = (
        f"以下是{len(candidate_indices)}个段落和一个问题。请对每个段落与问题的相关性打分（1-10）。\n\n"
        f"问题：{query}\n\n"
        f"{numbered}\n\n"
        "严格按以下格式输出，每行一个，不要有任何其他文字：\n"
        "段落编号:分数\n"
    )

    resp = client.chat.completions.create(
        model="glm-4-flash",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    text = resp.choices[0].message.content.strip()
    scored = []
    for line in text.split("\n"):
        line = line.strip()
        if ":" not in line:
            continue
        parts = line.split(":", 1)
        try:
            raw = parts[0].strip()
            for prefix in ("段落", "片段", "["):
                if raw.startswith(prefix):
                    raw = raw[len(prefix):]
                    break
            raw = raw.rstrip("]").strip()
            idx = int(raw)
            score = float(parts[1].strip())
            if idx in candidate_indices:
                scored.append((idx, score))
        except (ValueError, IndexError):
            continue
    if not scored:
        return candidate_indices[:top_k]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [idx for idx, _ in scored[:top_k]]


def generate_answer(client: OpenAI, question: str, contexts: list[str]) -> str:
    context_text = "\n".join(f"- {c}" for c in contexts)
    prompt = (
        f"请根据以下上下文回答问题。只使用上下文中的信息，不要编造。\n\n"
        f"上下文：\n{context_text}\n\n"
        f"问题：{question}\n\n"
        f"答案："
    )
    resp = client.chat.completions.create(
        model="glm-4-flash",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return resp.choices[0].message.content.strip()


def main():
    print("RAGAS 对比评估 Demo: Naive RAG vs Reranked RAG")
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

    print("步骤 1: 构建知识库向量索引...")
    embed_model = LCOpenAIEmbeddings(
        model="embedding-3",
        openai_api_key=ZHIPU_API_KEY,
        openai_api_base=ZHIPU_BASE_URL,
    )
    doc_embeddings = embed_model.embed_documents(KNOWLEDGE_BASE)
    print(f"  知识库: {len(KNOWLEDGE_BASE)} 个片段")

    print("\n步骤 2: 两种检索策略生成答案...")
    naive_samples = []
    reranked_samples = []

    for q_data in QUESTIONS:
        question = q_data["question"]
        reference = q_data["reference"]

        query_emb = embed_model.embed_query(question)

        naive_indices = naive_retrieve(query_emb, doc_embeddings, top_k=2)
        naive_contexts = [KNOWLEDGE_BASE[i] for i in naive_indices]
        naive_answer = generate_answer(client, question, naive_contexts)

        candidate_indices = naive_retrieve(query_emb, doc_embeddings, top_k=5)
        reranked_indices = rerank_with_llm(client, question, KNOWLEDGE_BASE, candidate_indices, top_k=2)
        reranked_contexts = [KNOWLEDGE_BASE[i] for i in reranked_indices]
        reranked_answer = generate_answer(client, question, reranked_contexts)

        naive_samples.append(SingleTurnSample(
            user_input=question,
            response=naive_answer,
            reference=reference,
            retrieved_contexts=naive_contexts,
        ))
        reranked_samples.append(SingleTurnSample(
            user_input=question,
            response=reranked_answer,
            reference=reference,
            retrieved_contexts=reranked_contexts,
        ))

        print(f"\n  问题: {question}")
        print(f"  Naive 检索: {[KNOWLEDGE_BASE[i][:30] + '...' for i in naive_indices]}")
        print(f"  Reranked 检索: {[KNOWLEDGE_BASE[i][:30] + '...' for i in reranked_indices]}")

    metrics = [
        Faithfulness(llm=llm),
        ResponseRelevancy(llm=llm, embeddings=embeddings, strictness=1),
        ContextPrecision(llm=llm),
        ContextRecall(llm=llm),
    ]

    print("\n步骤 3: RAGAS 评估 Naive RAG...")
    naive_dataset = EvaluationDataset(samples=naive_samples)
    naive_result = evaluate(
        dataset=naive_dataset,
        metrics=metrics,
        llm=llm,
        embeddings=embeddings,
        show_progress=True,
    )

    print("\n步骤 4: RAGAS 评估 Reranked RAG...")
    reranked_dataset = EvaluationDataset(samples=reranked_samples)
    reranked_result = evaluate(
        dataset=reranked_dataset,
        metrics=metrics,
        llm=llm,
        embeddings=embeddings,
        show_progress=True,
    )

    naive_df = naive_result.to_pandas()
    reranked_df = reranked_result.to_pandas()

    print("\n" + "=" * 60)
    print("对比评估结果")
    print("=" * 60)

    metric_cols = [c for c in naive_df.columns if c not in ("user_input", "response", "reference", "retrieved_contexts")]

    print(f"\n{'指标':<25} {'Naive RAG':>12} {'Reranked RAG':>12} {'差异':>10}")
    print("-" * 60)
    for col in metric_cols:
        naive_avg = naive_df[col].mean()
        reranked_avg = reranked_df[col].mean()
        diff = reranked_avg - naive_avg
        arrow = "+" if diff > 0 else ""
        print(f"  {col:<23} {naive_avg:>12.4f} {reranked_avg:>12.4f} {arrow}{diff:>9.4f}")

    cp_naive = naive_df["context_precision"].mean()
    cp_reranked = reranked_df["context_precision"].mean()
    print(f"\nContext Precision: Naive={cp_naive:.4f}, Reranked={cp_reranked:.4f}")
    if cp_reranked >= cp_naive:
        print("验证通过: Reranked RAG 在 context_precision 上得分 >= Naive RAG")
    else:
        print("警告: Reranked 未如预期提升 context_precision（样本量小，LLM 评分有波动）")


if __name__ == "__main__":
    main()
