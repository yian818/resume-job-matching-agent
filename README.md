# 简历-岗位撮合智能体

基于 LangGraph + SQLite + Pydantic 构建的 AI 招聘 Agent，实现简历信息结构化抽取、岗位匹配打分、条件分支判断全流程。

## 功能特性

- **简历信息抽取**：使用 Pydantic `with_structured_output` 强制大模型输出结构化简历信息，避免 JSON 解析错误
- **条件分支判断**：LangGraph conditional_edges，简历信息完整则匹配岗位打分，不完整则走追问流程
- **岗位数据库**：SQLite 存储岗位信息，支持多岗位多维度匹配
- **匹配报告生成**：大模型输出 markdown 格式评估报告，包含匹配度评分、理由和短板分析

## 项目结构

```
resume-job-matching-agent/
├── main.py          # 主程序入口，LangGraph 状态图编排
├── state.py         # AgentState 状态定义
├── nodes.py         # 节点函数：简历抽取、岗位匹配、追问
└── database.py      # SQLite 岗位数据库初始化与查询
```

## 快速开始

### 1. 安装依赖

```bash
pip install langgraph langchain-openai pydantic openai
```

### 2. 配置 API

在 `nodes.py` 中配置大模型 API：

```python
llm = ChatOpenAI(
    model="deepseek-chat",
    base_url="https://api.deepseek.com/v1",
    api_key="你的API Key",
    temperature=0.1
)
```

### 3. 初始化数据库

```bash
python database.py
```

### 4. 运行

```bash
python main.py
```

## 技术栈

| 技术 | 用途 |
|---|---|
| LangGraph | Agent 状态图编排，节点+条件分支 |
| LangChain OpenAI | 大模型调用，兼容 OpenAI 接口 |
| Pydantic | 结构化输出约束，类型安全 |
| SQLite | 岗位数据存储 |

## Agent 流程图

```
简历文本输入
    ↓
[抽取简历信息] ← Pydantic 结构化输出
    ↓
信息完整？
    ├─ 是 → [岗位匹配打分] → 输出评估报告
    └─ 否 → [追问用户补充信息]
```

## 匹配维度

- 学历匹配
- 技能匹配（Python / LangGraph / LLM / RAG 等）
- 工作年限要求
- 项目经验相关性
- 综合评分（0-100）

## 示例输出

```
=== 节点1：抽取简历信息 ===
信息完整度：False
抽取成功：{'name': '李博文', 'education': '本科', ...}
=== 节点2：岗位匹配打分 ===
报告生成完成

# 招聘岗位匹配评估报告

## 3. 岗位匹配列表
| 岗位 | 部门 | 匹配度 | 结论 |
|---|---|---:|---|
| AI评测工程师 | AI产品部 | 75/100 | 技能高度匹配 |
| AI产品经理 | 产品部 | 55/100 | 部分可迁移 |
| 后端开发工程师 | 技术部 | 25/100 | 技术栈不匹配 |
```

## License

MIT
