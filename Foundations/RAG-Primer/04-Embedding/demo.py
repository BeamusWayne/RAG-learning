"""04-Embedding demo: embedder 选型与 "归一化、对称、维度" 三件事。

演示要点：
    - 用 .env 里配的 embedder（Ollama 优先，否则 sentence-transformers）打印同义/异义句相似度
    - 对比 L2 归一化前后的得分差异
    - 演示非对称查询（短 query → 长 doc）的排名
    - Matryoshka 风格的"截断到 N 维"对召回的影响

模型 / API 配置全部走仓库根 .env。
运行：
    uv run python Foundations/RAG-Primer/04-Embedding/demo.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

from _common import cosine, get_embedder, need, section  # noqa: E402


SENTENCES = [
    "如何申请退款",
    "怎么把钱要回来",
    "退货流程是什么样的",
    "今天天气真好",
    "猫咪喜欢晒太阳",
]

DOCS = [
    "用户提交退款申请后，财务在 3 个工作日内审核并原路退回。",
    "退货流程：在订单页点'申请退货'，上传凭证，等待审核后寄回商品。",
    "本地天气以多云为主，最高气温 24 摄氏度。",
    "猫的体温大约在 38~39 摄氏度，比人类高。",
]


def show_matrix(labels: list[str], mat: np.ndarray) -> None:
    head = " " * 12 + "  ".join(f"{l[:6]:>6}" for l in labels)
    print(head)
    for r, lr in enumerate(labels):
        row = "  ".join(f"{mat[r, c]:>6.3f}" for c in range(len(labels)))
        print(f"  {lr[:10]:<10}  {row}")


def main() -> None:
    embedder = get_embedder()
    need(embedder, "embedder（Ollama 或 sentence-transformers）")
    print(f"embedder = {embedder.backend} / {embedder.model}")

    section("1) 句间相似度（已 L2 归一化）")
    v = embedder(SENTENCES, normalize=True)
    show_matrix(SENTENCES, cosine(v, v))
    print("  期望：'退款 / 要回来 / 退货流程' 三者相互高于'天气 / 猫咪'。")

    section("2) 归一化的影响")
    v_raw = embedder(SENTENCES, normalize=False)
    v_norm = embedder(SENTENCES, normalize=True)
    print(f"  未归一化向量范数: {np.linalg.norm(v_raw, axis=1).round(3).tolist()}")
    raw_scores = (v_raw[0] * v_raw).sum(axis=1)
    norm_scores = (v_norm[0] * v_norm).sum(axis=1)
    print("  以第 0 句为 query，未归一化（内积）vs 归一化（cosine）的得分:")
    for i, s in enumerate(SENTENCES):
        print(f"    [{i}] raw={raw_scores[i]:>8.3f}  cos={norm_scores[i]:>6.3f}  | {s}")
    print("  规则：所有 embedding 入库前一律 L2 归一化，再用 cosine。")

    section("3) 非对称查询（短 query → 长 doc）")
    q = "怎么退钱"
    s = cosine(embedder([q]), embedder(DOCS))[0]
    for rank, idx in enumerate(np.argsort(-s), 1):
        print(f"    rank {rank}  score={s[idx]:.3f}  doc[{idx}] {DOCS[idx][:40]}")
    print("  关键：生产 RAG 多是非对称（query 短、doc 长），尽量用文档检索专用模型。")

    section("4) Matryoshka 维度截断")
    full = embedder(SENTENCES, normalize=True)
    qv = embedder(["如何申请退款"], normalize=True)
    print(f"  原始维度 D = {full.shape[1]}")
    for d in (1024, 768, 512, 384, 256, 128, 64):
        if d > full.shape[1]:
            continue
        f_d = full[:, :d]
        f_d = f_d / np.clip(np.linalg.norm(f_d, axis=1, keepdims=True), 1e-12, None)
        q_d = qv[:, :d]
        q_d = q_d / np.clip(np.linalg.norm(q_d, axis=1, keepdims=True), 1e-12, None)
        sims = (q_d @ f_d.T)[0]
        top = int(np.argmax(sims))
        print(f"    截到 {d:>4} 维  top1=[{top}] {SENTENCES[top][:14]:<14}  score={sims[top]:.3f}")
    print("  Matryoshka 训练的模型可任意截维；非 MRL 模型截太狠会掉点。")


if __name__ == "__main__":
    main()
