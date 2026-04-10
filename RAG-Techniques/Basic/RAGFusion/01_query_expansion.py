"""
Step 1 — 查询扩展（Query Expansion）
======================================
RAG Fusion 的第一步：把一个问题扩展成多个角度的子查询。

核心思路：
  同一个问题，不同表述 → 检索到不同文档 → 覆盖面更广

本文件只关注"扩展"这一步，不做检索。
运行后可以直观看到 LLM 如何理解并改写你的问题。

运行：
  export OPENAI_API_KEY=...
  uv run python 01_query_expansion.py
"""

import os

from openai import OpenAI

CHAT_MODEL = "gpt-5.4"


def make_client() -> OpenAI:
    kwargs: dict = {}
    if base := os.environ.get("OPENAI_BASE_URL"):
        kwargs["base_url"] = base
    return OpenAI(**kwargs)


def expand_query(client: OpenAI, question: str, n: int = 4) -> list[str]:
    """
    用 LLM 把一个问题扩展成 n 个不同角度的子查询。

    扩展策略：
    - 换用不同关键词表述同一问题
    - 拆解成更具体的子问题
    - 考虑用户可能隐含的需求
    """
    prompt = (
        f"请把下面的问题改写成 {n} 个不同角度的搜索查询，"
        "每个查询用不同的关键词或句式表达相同的信息需求。\n"
        "直接输出查询列表，每行一条，不加编号或标点。\n\n"
        f"原始问题：{question}"
    )
    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,  # 适当提高随机性，让扩展更多样
    )
    raw = resp.choices[0].message.content.strip()
    queries = [line.strip() for line in raw.splitlines() if line.strip()]
    return queries[:n]  # 防止模型输出超过 n 条


def main() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("请先设置环境变量 OPENAI_API_KEY。")

    client = make_client()

    question = input("请输入问题（直接回车使用默认）：").strip()
    if not question:
        question = "RAG 系统的检索质量差怎么优化？"

    print(f"\n原始问题：{question}")
    print("\n正在扩展查询...\n")

    queries = expand_query(client, question, n=4)

    print("扩展后的查询变体：")
    for i, q in enumerate(queries, 1):
        print(f"  [{i}] {q}")

    print(f"\n共生成 {len(queries)} 个子查询。")
    print("下一步：用每个子查询分别检索 → 02_rrf_algorithm.py 展示如何合并结果。")


if __name__ == "__main__":
    main()
