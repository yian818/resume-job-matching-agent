# 简历-岗位智能匹配 Agent

基于 **LangGraph + RAG + FastAPI** 构建的 AI 招聘助手，实现简历结构化抽取、语义检索、岗位匹配打分、Human-in-the-loop 追问全流程。

## ✨ 功能特性

- **简历结构化抽取**：Pydantic 强约束 + 三层降级解析，字段准确率 98.5%
- **RAG 语义检索**：ChromaDB + BGE-large-zh-v1.5，解决关键词匹配不上的问题
- **混合检索架构**：SQL 硬过滤 → RAG 向量召回 Top-5 → LLM 精排打分
- **Human-in-the-loop**：信息缺失时暂停执行，追问用户补充后继续
- **Web 服务**：FastAPI 封装 RESTful 接口，支持在线测试
- **评测体系**：50 份人工标注简历测试集，Top-1 命中率 91.2%

## 🏗️ 项目架构

```
用户输入简历
    ↓
[节点1：简历抽取] ← Pydantic 结构化输出
    ↓
信息完整？
    ├─ 否 → [Human-in-the-loop追问] → 重新抽取
    └─ 是
        ↓
[SQL硬过滤] ← 年限不满足的岗位直接排除
        ↓
[RAG语义检索] ← ChromaDB + BGE 召回 Top-5
        ↓
[节点2：LLM精排打分] ← 0-100分 + 理由
        ↓
[节点3：简历优化建议] ← STAR原则扩写
        ↓
[节点4：模拟面试题] ← 技术题+项目题
        ↓
输出完整报告
```

## 📁 项目结构

```
Resume-Job Matching Agent/
├── main.py              # LangGraph 主流程编排
├── main_api.py          # FastAPI Web服务
├── nodes.py             # 节点函数（抽取/匹配/追问/优化/面试题）
├── state.py             # AgentState 状态定义
├── retriever.py         # RAG语义检索层（ChromaDB + BGE）
├── database.py          # SQLite 岗位数据库
├── resume_parser.py     # PDF简历解析
├── scoring_rules.py     # 打分规则配置
├── db_queries.py        # SQL查询练习
│
├── docs/                # 文档
│   ├── PROJECT_LOG.md   # 项目迭代日志（16个bug记录+面试话术）
│   ├── PROJECT_STRUCTURE.md
│   └── 项目交接文档.md
│
├── data/                # 数据文件
│   ├── jobs.db          # SQLite岗位数据库
│   ├── chroma_db/       # ChromaDB向量库
│   └── agent.log        # 运行日志
│
└── eval/                # 评测脚本
    ├── eval_dataset.py  # 50份简历测试集
    ├── eval_runner.py   # Step1抽取评测
    ├── eval_match_v2.py # Step2匹配评测
    ├── manual_answers.json # 人工标注标准答案
    └── import_jobs.py   # 导入岗位到数据库
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API

创建 `.env` 文件：

```env
MODEL_NAME=deepseek-chat
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_API_KEY=你的API Key
temperature=0.1
```

### 3. 运行命令行版本

```bash
python main.py
```

### 4. 启动 Web 服务

```bash
python main_api.py
```

访问 `http://localhost:8000/docs` 在线测试接口。

## 📊 评测结果

### 简历抽取评测（50份）

| 字段 | 准确率 |
|---|---|
| 姓名 | 100% |
| 学历 | 100% |
| 工作年限 | 98% |
| 技能 | 95.9% |
| **总体** | **98.5%** |

### 岗位匹配评测（34份人工标注）

| 指标 | 结果 |
|---|---|
| Top-1 命中率 | 91.2% |
| Top-3 命中率 | 97.1% |

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
