# 简历-岗位智能匹配 Agent（ResumeMatch AI）

基于 **LangGraph + RAG + FastAPI** 构建的 AI 招聘助手，实现简历结构化抽取、语义检索、岗位匹配打分、可解释报告，并配有**现代化 Web 前端**与 **Docker 一键部署**。

## ✨ 功能特性

- **简历结构化抽取**：Pydantic 强约束 + 三层降级解析 + 确定性技能补抽，抽取漏抽率 0%
- **混合检索架构**：SQL 硬过滤 → RAG 向量召回（ChromaDB + BGE-large-zh-v1.5）→ 关键词补足
- **四信号融合打分**：规则引擎 + LLM + cross-encoder 重排 + 职业身份，硬上限兜底防翻车
- **可解释报告**：每个岗位解读 为什么（技能命中/缺口、职业身份、硬上限），总评段落确定性生成、零 LLM 幻觉风险
- **在线评测台**（`/eval`）：拖动四信号权重，Top-1 / MRR / NDCG 即时刷新；四信号原值缓存，融合层纯函数重算，调参不烧 LLM
- **稳定性评估**：同一简历重复跑 N 次，量化 Top-1 翻转率与标答跨重复命中率
- **Web 前端**：深色玻璃拟态 UI，粘贴/拖拽简历即出匹配报告（纯静态，无构建）
- **API 鉴权**：Bearer Token，Docker 一键部署
- **评测体系**：50 份人工标注简历测试集，**Top-1 98%、Top-3 100%、MRR 0.99**

## 🏗️ 项目架构

```
用户输入简历
    ↓
[节点1：简历抽取] ← Pydantic 结构化输出 + 原文技能补抽
    ↓
[SQL硬过滤] ← 年限不满足的岗位直接排除
    ↓
[RAG语义检索] ← ChromaDB + BGE 召回 Top-10 + 关键词补足
    ↓
[节点2：LLM精排打分] ← 0-100分 + 理由 + 职业身份优先
    ↓
[四信号融合] ← min(0.4×规则 + 0.3×LLM + 0.3×重排, 硬上限)
    ↓
[输出] ← 岗位排行 + 理由 + 四信号明细
```

## 📁 项目结构

```
Resume-Job Matching Agent/
├── main.py              # LangGraph 主流程编排
├── main_api.py          # FastAPI Web服务（结构化API + 鉴权）
├── nodes.py             # 节点函数（抽取/匹配/补抽）
├── explain.py           # 可解释报告层（确定性解读，零LLM）
├── state.py             # AgentState 状态定义
├── retriever.py         # RAG语义检索层（ChromaDB + BGE）
├── database.py          # SQLite 岗位数据库
├── scoring_rules.py     # 规则引擎 + 职业身份匹配 + 硬上限
├── reranker.py          # cross-encoder 语义重排
├── static/              # Web 前端（index.html / styles.css / app.js / eval.html / eval.js）
├── Dockerfile           # 生产镜像
├── docker-compose.yml   # 一键启动
├── requirements.txt
│
├── docs/
│   ├── PROJECT_LOG.md   # 项目迭代日志（每阶段现象/原因/修复/面试话术）
│   └── PROJECT_STRUCTURE.md
│
├── data/                # SQLite + ChromaDB 向量库
│
└── eval/                # 评测体系
    ├── eval_dataset.py      # 50份简历 + 54岗位库
    ├── manual_answers.json  # 人工标注标准答案
    ├── eval_match_v2_batch.py # 分批评测（断点续跑）
    ├── metrics.py           # MRR / NDCG 排序质量指标
    ├── stability_eval.py    # 排序稳定性评测（Top-1翻转率）
    ├── eval_cache.py        # 在线评测台：四信号缓存 + 权重模拟（纯函数）
    ├── check_explain.py     # 解释层回归测试
    ├── smoke_p12_api.py     # HTTP 冒烟（验证 /api/v1/match 返回 explanation）
    ├── label_audit_v3.py    # 标答 vs 简历客观事实复核
    ├── diagnose_cases.py    # 四信号诊断
    └── import_jobs.py       # 导入岗位到数据库
```

## 🚀 快速开始

### 方式一：Docker 一键启动（推荐）

```bash
# 1. 配置环境变量（把 API Key 填进 .env）
cp .env.example .env

# 2. 一键启动（首次构建拉模型约需几分钟）
docker compose up --build
```

访问 `http://localhost:8000` 打开前端页面。

### 方式二：本地运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 .env
cp .env.example .env   # 填 OPENAI_API_KEY

# 3. 导入岗位库（初始化 SQLite + 向量库）
python eval/import_jobs.py

# 4. 启动 Web 服务
python main_api.py
```

访问 `http://localhost:8000` 打开前端，`http://localhost:8000/docs` 查看 API。

### API 鉴权

配置了 `.env` 里的 `API_TOKEN` 后，调用 `/api/v1/*` 需带请求头：

```bash
curl -X POST http://localhost:8000/api/v1/match \
  -H "Authorization: Bearer <API_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"resume_text":"..."}'
```

未配置 `API_TOKEN` 时本地开发直接放行。前端右上角可填 Token（存 localStorage）。

响应结构：`candidate` 候选人画像 · `matches` 岗位排行（含四信号明细）· `explanation` 可解释报告（Top-1 总评 + 逐岗位解读：技能命中/缺口、职业身份、年限、学历、硬上限）。

**稳定性配置**（可选，P13）：`LLM_TEMPERATURE`（默认 0.1）与 `SCORE_RUNS`（默认 1）两个开关。实测 `temp0 + SCORE_RUNS=3` 能把分数波动从 ±6 压到 ±1，但**没有消除**近分岗位的 Top-1 翻转（标答集翻转 1/5 → 2/5，瓶颈在抽取层方差），因此默认关闭；完整数据见 `eval/stability_*.json` 与 `docs/PROJECT_LOG.md` P13。

## 📊 评测结果（50 份人工标注简历，客观标答）

| 指标 | 结果 |
|---|---|
| Top-1 命中率 | **98.0%**（49/50） |
| Top-3 命中率 | **100.0%**（50/50） |
| MRR（平均倒数排名） | **0.990** |
| NDCG@3 | **0.993** |
| 召回率 | 100% |
| 抽取漏抽率 | 0% |

## 🛠️ 技术栈

| 技术 | 用途 |
|---|---|
| LangGraph | Agent 状态图编排，节点+条件分支+循环 |
| FastAPI | Web 服务，RESTful API |
| Pydantic | 结构化输出约束，类型安全 |
| ChromaDB | 向量数据库，RAG语义检索 |
| BGE-large-zh-v1.5 | 中文嵌入模型 |
| SQLite | 岗位数据存储 |
| DeepSeek LLM | 大模型调用 |

## 📝 面试亮点

> "我用评测驱动开发的方式做这个项目：
>
> 1. **第一步：简历抽取评测** - 建了50份测试集，准确率98.5%
> 2. **第二步：岗位匹配评测** - 人工标注标准答案，Top-1命中率91.2%
> 3. **第三步：加RAG语义检索层** - ChromaDB + BGE，解决关键词匹配问题
> 4. **第四步：Human-in-the-loop** - 信息缺失时追问用户补充
> 5. **第五步：FastAPI部署** - 封装成Web服务
>
> 整个过程就是MLOps的思路：用数据驱动优化，而不是凭感觉改。"

## License

MIT
