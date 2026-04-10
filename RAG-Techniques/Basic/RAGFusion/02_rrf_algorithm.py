"""
Step 2 — RRF 算法（Reciprocal Rank Fusion）
============================================
RAG Fusion 的核心：把多个检索结果列表合并成一个排序。

RRF 公式：
  score(doc) = Σ  1 / (k + rank_i(doc))
               i
  其中 k=60 是平滑常数（防止第1名权重过高），rank 从 1 开始。

本文件纯算法演示，不调用 LLM 也不需要向量库，
用一个玩具示例说明 RRF 如何把多路检索结果融合。

运行：
  uv run python 02_rrf_algorithm.py
  （无需 API Key）
"""

from dataclasses import dataclass, field


@dataclass
class RRFFusion:
    """
    互惠排名融合（Reciprocal Rank Fusion）

    参数：
      k: 平滑常数，默认 60（原论文推荐值）
         - k 越小，第1名优势越大
         - k 越大，各名次差距越小（更"民主"）
    """

    k: int = 60
    scores: dict[str, float] = field(default_factory=dict)

    def add_ranked_list(self, ranked_docs: list[str]) -> None:
        """输入一个排好序的文档列表（index=0 是第1名），更新 RRF 得分。"""
        for rank, doc in enumerate(ranked_docs, start=1):
            self.scores[doc] = self.scores.get(doc, 0.0) + 1.0 / (self.k + rank)

    def get_fused_ranking(self) -> list[tuple[str, float]]:
        """返回按 RRF 得分降序排列的 (doc, score) 列表。"""
        return sorted(self.scores.items(), key=lambda x: x[1], reverse=True)


def print_ranked_list(title: str, docs: list[str]) -> None:
    print(f"\n{title}")
    for i, doc in enumerate(docs, 1):
        print(f"  #{i}  {doc}")


def main() -> None:
    # ── 模拟三路检索结果（同一知识库，三个不同查询各返回一个排序列表）──────
    #
    # 背景：用户问"RAG 检索质量差怎么优化？"，扩展出3个子查询：
    #   查询A："RAG 检索精度低 解决方案"
    #   查询B："向量检索召回率不足"
    #   查询C："如何提升 RAG 相关性"
    #
    # 每个查询返回的 Top-5 文档（顺序不同）：

    results_a = [
        "文档1：使用重排序（Reranking）提升检索精度",
        "文档2：查询改写可提高检索相关性",
        "文档3：混合检索（BM25 + 向量）覆盖更全面",
        "文档4：调整 chunk 大小改善上下文完整性",
        "文档5：增加知识库文档数量扩大覆盖",
    ]

    results_b = [
        "文档3：混合检索（BM25 + 向量）覆盖更全面",   # 在 B 中排第1
        "文档6：Top-K 设置过小导致召回率低",
        "文档1：使用重排序（Reranking）提升检索精度",  # 在 B 中排第3
        "文档7：嵌入模型选择影响语义理解能力",
        "文档4：调整 chunk 大小改善上下文完整性",
    ]

    results_c = [
        "文档2：查询改写可提高检索相关性",             # 在 C 中排第1
        "文档1：使用重排序（Reranking）提升检索精度",  # 在 C 中排第2
        "文档8：使用 HyDE 假设文档提升检索命中率",
        "文档3：混合检索（BM25 + 向量）覆盖更全面",
        "文档9：向量归一化对余弦相似度的影响",
    ]

    print_ranked_list("查询A 检索结果：", results_a)
    print_ranked_list("查询B 检索结果：", results_b)
    print_ranked_list("查询C 检索结果：", results_c)

    # ── 执行 RRF 融合 ─────────────────────────────────────────────────────
    fusion = RRFFusion(k=60)
    fusion.add_ranked_list(results_a)
    fusion.add_ranked_list(results_b)
    fusion.add_ranked_list(results_c)

    fused = fusion.get_fused_ranking()

    print("\n" + "─" * 55)
    print("  RRF 融合后的排序（附得分）")
    print("─" * 55)
    for i, (doc, score) in enumerate(fused, 1):
        # 标注在几路结果里出现过
        appearances = sum(
            doc in r for r in [results_a, results_b, results_c]
        )
        tag = f"出现 {appearances} 次" if appearances > 1 else "仅出现 1 次"
        print(f"  #{i}  {doc}")
        print(f"       得分={score:.4f}  [{tag}]")

    # ── 关键观察 ─────────────────────────────────────────────────────────
    print("\n── 关键观察 ──────────────────────────────────────────")
    print("文档1 在三路结果中分别排 #1、#3、#2 → RRF 得分最高，排融合第1名")
    print("文档3 在三路结果中分别排 #3、#1、#4 → 多次出现，稳定排在前列")
    print("文档9 只在查询C 中出现且排最后 → RRF 得分最低")
    print("\n结论：RRF 奖励'多路一致认可'的文档，而非单路排名很高的文档。")

    # ── 演示 k 值的影响 ───────────────────────────────────────────────────
    print("\n── k 值影响演示（以文档1 和文档6 为例）────────────────")
    for k in [1, 10, 60, 100]:
        f = RRFFusion(k=k)
        f.add_ranked_list(results_a)
        f.add_ranked_list(results_b)
        f.add_ranked_list(results_c)
        ranked = f.get_fused_ranking()
        top3 = [doc.split("：")[0] for doc, _ in ranked[:3]]
        print(f"  k={k:3d}  Top-3: {top3}")


if __name__ == "__main__":
    main()
