# Resume-Job Matching Agent 项目结构

## 📁 项目框架

```
Resume-Job Matching Agent/
│
├── 📂 核心代码（Agent主流程）
│   ├── main.py              # LangGraph主流程编排（入口）
│   ├── nodes.py             # 节点函数：简历抽取、岗位匹配打分、追问、优化建议
│   ├── state.py             # AgentState状态定义（TypedDict）
│   ├── database.py          # SQLite岗位数据库操作
│   ├── resume_parser.py     # PDF简历文本解析
│   ├── retriever.py         # RAG语义检索层（ChromaDB+BGE）
│   └── scoring_rules.py    # 打分规则权重配置
│
├── 📂 评测体系（P1阶段成果）
│   ├── eval_dataset.py      # 50份简历+20个JD测试集（Python版）
│   ├── eval_dataset.json    # 测试集JSON版
│   ├── eval_runner.py       # Step1：简历结构化抽取评测
│   ├── eval_match.py        # Step2：岗位匹配评测v1（关键词交集标准答案）
│   ├── eval_match_v2.py     # Step2：岗位匹配评测v2（人工标注标准答案）
│   ├── manual_answers.json  # 人工标注标准答案（34份简历的正确岗位）
│   ├── eval_report.json      # Step1评测结果报告
│   └── import_jobs.py       # 导入20个JD到SQLite数据库
│
├── 📂 配置文件
│   ├── .env                 # API密钥配置（DeepSeek）
│   ├── .gitignore           # Git忽略规则
│   └── requirements.txt     # 依赖列表（待生成）
│
├── 📂 文档
│   ├── PROJECT_LOG.md       # 项目迭代日志（所有bug和修复记录）
│   ├── 项目交接文档.md       # 项目交接说明
│   └── 匹配报告.md           # 匹配输出报告示例
│
└── 📂 数据文件（自动生成）
    ├── jobs.db             # SQLite岗位数据库
    ├── agent.log            # 运行日志
    ├── chroma_db/          # ChromaDB向量库（RAG用）
    └── test_output.txt     # 测试输出
```

---

## 🔄 Agent工作流

```
上传简历PDF
    ↓
[节点1] 简历抽取（extract_resume_node）
    - Pydantic结构化输出
    - 提取：姓名/学历/年限/技能/项目
    ↓
    ├── 信息不完整 → [追问节点] ask_more_node
    └── 信息完整 ↓
[节点2] 岗位匹配打分（match_jobs_node）
    - RAG语义检索Top-5相关岗位
    - 大模型精确打分（0-100分）
    ↓
[节点3] 简历优化建议（resume_optimize_node）
    ↓
[节点4] 模拟面试题生成（interview_question_node）
    ↓
输出Markdown匹配报告
```

---

## 📊 评测结果

| 评测项 | 指标 | 结果 |
|---|---|---|
| 简历抽取准确率 | 总体字段 | 98.5% |
| 姓名识别 | - | 100% |
| 学历识别 | - | 100% |
| 年限识别 | - | 98% |
| 技能识别 | - | 95.9% |
| 岗位匹配Top-1命中率 | 人工标注答案 | 91.2% |
| 岗位匹配Top-3命中率 | 人工标注答案 | 97.1% |

---

## 🚀 技术栈

- **Agent框架**：LangGraph（状态图+条件分支）
- **大模型**：DeepSeek（via OpenAI兼容API）
- **结构化输出**：Pydantic with_structured_output
- **向量检索**：ChromaDB + BGE-large-zh-v1.5
- **数据库**：SQLite
- **日志**：Python logging
