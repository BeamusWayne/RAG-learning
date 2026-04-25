# MultiLevelRAG — 多层级 RAG 对比平台

> 意图感知路由 × 五种 RAG 策略 × Streamlit 交互界面

---

## 项目简介

MultiLevelRAG 是在 RAG-learning 仓库中构建的**生产级多策略 RAG 对比系统**，核心能力：

1. **意图路由器**：LLM 自动识别问题类型，分配最合适的 RAG 策略
2. **五种 RAG 策略**：Baseline / HyDE / RAG Fusion / CRAG / GraphRAG
3. **全策略并行对比**：同一问题并发执行所有策略，横向比较答案质量与耗时
4. **知识图谱**：NetworkX 轻量图谱，无需 Neo4j，自动抽取实体关系
5. **Streamlit 前端**：赛博朋克暗色主题，支持文档上传、策略对比、流程可视化

---

## 系统架构

```
用户问题
    │
    ▼
┌─────────────────────────────────────────────────┐
│              Intent Router (router.py)           │
│  LLM 分类 → baseline | hyde | fusion | crag | graph  │
└──────┬──────────┬───────────┬─────────┬─────────┘
       │          │           │         │         │
  Baseline     HyDE      Fusion      CRAG     GraphRAG
  RAG          RAG       RAG
  (baseline_   (hyde_    (fusion_    (crag.  (graph_
   rag.py)      rag.py)   rag.py)    py)      rag.py)
       │          │           │         │         │
       └──────────┴───────────┴─────────┴─────────┘
                             │
                      统一结果格式 (dict)
                             │
                    evaluation/comparator.py
                             │
                       Streamlit app.py
```

---

## 五种策略详解

### 1. Baseline RAG
```
query → 向量检索 → 拼接上下文 → LLM 生成
```
**适用**: 精确事实查询、定义类问题  
**优点**: 最快，实现最简单  
**缺点**: 单路检索，query 质量直接决定结果

### 2. HyDE (Hypothetical Document Embeddings)
```
query → LLM 生成假设文档 → 假设文档向量检索 → LLM 生成
```
**适用**: 专业领域、query 较短但 passage 较长的场景  
**核心创新**: 用"假设答案"而非问题做检索，缩小语义鸿沟  
**来源**: Gao et al., 2022

### 3. RAG Fusion
```
query → LLM 扩展 N 子查询 → N 路并行检索 → RRF 融合排名 → LLM 生成
```
**适用**: 开放性、模糊、需要多角度探索的问题  
**核心创新**: RRF（Reciprocal Rank Fusion）融合多路检索结果  
**默认**: 3 子查询 + 原始查询 = 4 路检索

### 4. CRAG (Corrective RAG)
```
query → 检索 → 相关性评分 → 分支决策:
  ├─ Correct  (score > 0.5)  → 精炼内部知识 → 生成
  ├─ Incorrect(score < -0.9) → 网络搜索 → 生成
  └─ Ambiguous(介于两者)     → 内部精炼 + 外部搜索 → 生成
```
**适用**: 答案不确定、知识库覆盖不完整的场景  
**来源**: Yan et al., 2024

### 5. GraphRAG
```
文档索引: 文档 → LLM 抽取实体关系 → NetworkX 图谱
查询时:   query → 实体识别 → BFS 图遍历 → 向量检索
           → 向量上下文 + 图谱三元组 → LLM 生成
```
**适用**: 多实体关系推理、多跳问题  
**本实现**: 轻量版，无需 Neo4j，纯 Python NetworkX

---

## 与业界最佳实践对比

| 特性 | 本项目 | 业界最佳 |
|------|--------|---------|
| 意图路由 | LLM prompt 分类 | fine-tuned 分类器（更快） |
| Chunking | 固定大小 + 重叠 | 语义分块（更精准） |
| 检索 | 纯向量 | BM25 + 向量混合检索 |
| 重排序 | 无 | Cross-encoder reranker |
| 图谱 | NetworkX + LLM 抽取 | 专业 NER/RE 模型 |
| 评估 | 耗时对比 | RAGAS（忠实度/相关性/召回） |
| 流式输出 | 无 | SSE 流式 |

**待改进方向**：
- [ ] 加入 BM25 混合检索（`rank_bm25` 库）
- [ ] Cross-encoder 重排序（`sentence-transformers/ms-marco`）
- [ ] RAGAS 评估框架集成
- [ ] 流式输出支持

---

## 快速开始

### 环境要求
- Python 3.12+
- uv（推荐）或 pip

### 安装与配置

```bash
# 在仓库根目录
uv sync

# 配置 API Key（.env 已预置，按需修改）
cd Projects/MultiLevelRAG
# 编辑 .env:
# OPENAI_API_KEY=your_minimax_key
# OPENAI_BASE_URL=https://api.minimaxi.com/v1
# MULTI_RAG_LLM_MODEL=MiniMax-M2.5
# MULTI_RAG_EMBED_PROVIDER=dashscope   (MiniMax 无 embedding 端点)
```

### 启动

```bash
cd /path/to/RAG-learning
uv run streamlit run Projects/MultiLevelRAG/app.py
# 默认端口 8501，访问 http://localhost:8501
```

### 命令行快速测试

```bash
# 测试单个策略
uv run python -c "
import sys; sys.path.insert(0, 'Projects/MultiLevelRAG')
import config  # 自动加载 .env
from knowledge_loader import load_directory
load_directory('Projects/MultiLevelRAG/data')
from strategies.baseline_rag import run
r = run('什么是 RAG?')
print(r['answer'])
"

# 测试路由器
uv run python -c "
import sys; sys.path.insert(0, 'Projects/MultiLevelRAG')
import config
from router import route
print(route('GraphRAG 和 CRAG 有什么关系？'))
"
```

---

## 文件结构

```
Projects/MultiLevelRAG/
├── app.py                    # Streamlit 主应用（赛博朋克暗色 UI）
├── config.py                 # 全局配置（自动加载 .env）
├── router.py                 # 意图路由器（LLM 分类 → 策略选择）
├── knowledge_loader.py       # 文档加载（txt/pdf/md）→ 向量化
├── .env                      # API 配置（gitignored）
├── core/
│   ├── llm.py                # LLM 工厂（dashscope/openai/ollama）
│   ├── embeddings.py         # Embedding 工厂
│   └── vector_store.py       # Chroma 向量库
├── strategies/
│   ├── baseline_rag.py       # 标准 RAG
│   ├── hyde_rag.py           # HyDE
│   ├── fusion_rag.py         # RAG Fusion + RRF
│   ├── crag.py               # Corrective RAG
│   └── graph_rag.py          # GraphRAG (NetworkX)
├── evaluation/
│   └── comparator.py         # 全策略并发对比
└── data/
    └── sample_knowledge.txt  # 示例知识库（RAG 技术文档）
```

---

## LLM / Embedding 支持矩阵

| Provider | LLM | Embedding | 配置 |
|----------|-----|-----------|------|
| MiniMax | MiniMax-M2.5 ✓ | ✗ 不支持 | `MULTI_RAG_LLM_PROVIDER=openai` + `OPENAI_BASE_URL` |
| DashScope | qwen-plus ✓ | text-embedding-v3 ✓ | `MULTI_RAG_LLM_PROVIDER=dashscope` |
| OpenAI | gpt-4o ✓ | text-embedding-3 ✓ | `MULTI_RAG_LLM_PROVIDER=openai` |
| Ollama | qwen3:4b ✓ | nomic-embed-text ✓ | `MULTI_RAG_LLM_PROVIDER=ollama` |

> **推荐组合**: LLM=MiniMax-M2.5 + Embedding=DashScope text-embedding-v3

---

## Streamlit UI 说明

| 区域 | 功能 |
|------|------|
| 左侧 Sidebar | 文档上传/向量化、策略选择、运行模式、API 配置 |
| 问答 Tab | 单策略问答 + 路由结果展示 + 流程步骤 timeline |
| 策略对比 Tab | 多策略并发执行 + 耗时 metrics + 答案卡片网格 |
| 系统说明 Tab | 架构图、策略对比表、快速开始命令 |
