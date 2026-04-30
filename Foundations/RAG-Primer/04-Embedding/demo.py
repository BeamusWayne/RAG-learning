"""04-Embedding demo: 多个 embedding 模型在同一份语料上的召回对比。

骨架版本：仅打印模型列表。后续将填充：
    - bge-large-zh-v1.5 / OpenAI text-embedding-3-large / BGE-M3
    - 归一化前后对比
    - 对称 vs 非对称编码
    - Matryoshka 维度截断曲线

运行：
    uv run python Foundations/RAG-Primer/04-Embedding/demo.py
"""
from __future__ import annotations

MODELS: tuple[str, ...] = (
    "bge-large-zh-v1.5",
    "text-embedding-3-large",
    "BGE-M3",
)


def main() -> None:
    print("[04-Embedding] 骨架就位。")
    print(f"计划对比模型：{', '.join(MODELS)}")
    print("详见 ./README.md")


if __name__ == "__main__":
    main()
