# 项目迭代日志

> 记录每次迭代的问题、原因、修复方案和面试话术

---

## P0阶段：基础版搭建

### Bug 1：DeepSeek API认证失败

**现象**：调用API直接报401错误，说API Key无效。

**原因**：用了官方地址`api.deepseek.com`+旧Key，但这个Key是第三方代理平台的，不是官方的。

**修复**：换成第三方代理地址`https://nb.deepsb.com/v1`，Key从`.env`文件读取。

**面试话术**：
> "初版我直接用了DeepSeek官方API，但发现Key是代理平台的，连不上。我改成了从.env文件读取配置，支持切换不同的API地址，这样测试环境和生产环境可以用不同的Key，不用改代码。"

---

### Bug 2：Windows路径转义错误

**现象**：运行时报`SyntaxError: (unicode error) 'unicodeescape'`，指向PDF文件路径那一行。

**原因**：Windows路径里的反斜杠`\`被Python当成转义字符，比如`\U`被当成Unicode转义。

**修复**：路径前加`r`前缀变成原始字符串：`r"C:\Users\...\简历.pdf"`

**面试话术**：
> "Windows开发常见坑，路径里的反斜杠会被Python转义。我用r前缀解决，这是Windows开发的基本功。"

---

### Bug 3：大模型输出JSON不稳定

**现象**：有时候大模型返回`{...}`正常，有时候返回```json {...} ```代码块包裹，有时候返回Markdown列表，导致Pydantic校验失败。

**原因**：大模型是概率性输出，temperature=0.2也不能保证100%格式正确。

**修复**：加了三层降级：
1. 优先走`with_structured_output`结构化输出
2. 失败后手动调LLM，剥掉```json```代码块
3. 再失败就重试一次

```python
try:
    result = structured_llm.invoke(prompt)
except Exception:
    raw = llm.invoke(prompt).content
    raw = raw.replace("```json", "").replace("```", "").strip()
    result = ResumeInfo(**json.loads(raw))
```

**面试话术**：
> "我在评测中发现DeepSeek偶发返回markdown代码块包裹的JSON，导致Pydantic校验失败。我加了一层try-except降级：优先走structured output，失败后自动走raw调用+手动清洗，保证鲁棒性。这是生产环境必须做的，不能假设大模型每次都乖乖输出格式。"

---

### Bug 4：岗位分析遗漏

**现象**：岗位列表有3个，但大模型只分析了2个就停了。

**原因**：长文本注意力衰减，大模型处理长列表时容易漏最后几个。

**修复**：三层优化：
1. temperature从0.2降到0.1，降低随机性
2. 岗位列表从JSON改成编号文本格式（1. 岗位名...）
3. prompt里明确写"共N个岗位，必须逐个分析完"

**面试话术**：
> "初版测试发现大模型只分析了2个岗位就停了，这是长文本注意力衰减问题。我做了三层修复：温度调低、列表编号化、prompt里强调必须逐个分析完。修复后3个岗位全部覆盖。"

---

### Bug 5：条件分支不生效

**现象**：信息缺失时没有走追问节点，还是直接走了匹配节点。

**原因**：三个地方没对齐：
1. `state.py`里没有`info_complete`字段
2. `nodes.py`里没有判断逻辑
3. `main.py`里`add_conditional_edges`注册了但判断函数永远返回`match_jobs`

**修复**：
```python
# state.py 加字段
info_complete: bool

# nodes.py 加判断
state['info_complete'] = result.work_year > 0

# main.py 加条件分支
def should_match(state):
    return "match_jobs" if state['info_complete'] else "ask_more"

workflow.add_conditional_edges("extract_resume", should_match, {
    "match_jobs": "match_jobs",
    "ask_more": "ask_more"
})
```

**面试话术**：
> "条件分支没生效，我debug后发现是三层没对齐：state里没定义字段、node里没判断、graph里注册了但判断函数写死了。改完后测试：信息缺失走追问，信息完整走匹配，分支逻辑验证通过。LangGraph的条件分支关键是state字段要贯穿全链路。"

---

### Bug 6：API Key硬编码泄露风险

**现象**：第一次push把API Key传到GitHub了。

**原因**：Key直接写在`nodes.py`代码里，没做隔离。

**修复**：
1. 建`.env`文件存Key
2. `.gitignore`里忽略`.env`
3. 代码里用`os.getenv("OPENAI_API_KEY")`读取

**面试话术**：
> "我用.env文件管理敏感配置，.gitignore里忽略了.env，API Key不会传到GitHub。换Key只需要改.env文件，不用动代码。这是12-factor app的标准做法。"

---

## P1阶段：评测体系

### Bug 7：Pydantic中文键名映射

**现象**：大模型有时候返回`{"岗位名称": "AI工程师"}`而不是`{"job_title": "AI工程师"}`，导致Pydantic字段对不上。

**原因**：DeepSeek中文模型倾向于用中文键名。

**修复**：用Pydantic的`alias`参数：
```python
class JobMatchScore(BaseModel):
    job_title: str = Field(alias="岗位名称")
    score: int = Field(alias="匹配分数")
    reason: str = Field(alias="理由")
    
    class Config:
        populate_by_name = True
```

**面试话术**：
> "中文大模型经常返回中文键名，我用Pydantic的alias做了映射，既能接收中文键名也能接收英文键名，兼容性更好。"

---

### Bug 8：模型返回JSON数组而非对象

**现象**：大模型有时候直接返回`[{...}, {...}]`数组，而不是`{"matches": [{...}]}`对象。

**原因**：模型理解不一致，prompt里写的格式它没完全遵守。

**修复**：加`isinstance`判断：
```python
parsed = json.loads(text)
if isinstance(parsed, list):
    parsed = {"matches": parsed}
```

**面试话术**：
> "大模型有时候直接返回数组，我加了类型判断，如果是list就包装成dict，兼容两种输出格式。这是生产级代码必须做的容错。"

---

### Bug 9：f-string花括号转义

**现象**：prompt里写JSON示例，Python把`{`当成变量替换，运行报错。

**原因**：f-string里`{}`是变量占位符，JSON示例里的花括号会被误解。

**修复**：JSON示例里的花括号写成`{{}}`双花括号，Python会转义成单花括号。

**面试话术**：
> "f-string里写JSON示例有个坑，花括号会被当成变量。我用双花括号转义解决，这是Python字符串格式化的细节。"

---

### Bug 10：Windows GBK编码不认识特殊符号

**现象**：print输出✓✗等符号时报UnicodeEncodeError。

**原因**：Windows控制台默认GBK编码，不支持Unicode特殊符号。

**修复**：用ASCII替代（OK/XX），或者设置`PYTHONIOENCODING=utf-8`。

**面试话术**：
> "Windows控制台默认GBK编码，不认识特殊符号。我用ASCII替代解决，跨平台兼容性更好。"

---

### Bug 11：PowerShell输出重定向把日志当错误

**现象**：`python eval_match.py > eval_match_output.txt 2>&1`运行时，日志输出被PowerShell当成错误显示。

**原因**：PowerShell的错误处理机制，把stderr的内容当成异常显示。

**修复**：这是正常现象，日志确实在输出文件里，不影响评测结果。

**面试话术**：
> "Windows PowerShell和Linux bash的输出重定向行为不一样，日志会被当成错误流。这是环境差异，不是代码问题。"

---

## 评测结果记录

### P1-Step1：简历结构化抽取评测
- 测试集：50份简历
- 总体准确率：98.5%（193/196字段）
- name：100%
- education：100%
- work_year：98%
- skill：95.9%
- 平均耗时：6.9s/份

### P1-Step2：岗位匹配打分评测

**v1：关键词交集算标准答案**
- Top-1命中率：28%
- Top-3命中率：86%
- 问题：标准答案不准，很多简历被错误标注

**v2：人工标注标准答案（34份有明确匹配岗位的简历）**
- Top-1命中率：91.2%（31/34）
- Top-3命中率：97.1%（33/34）
- 结论：Agent实际表现很好，之前分数低是因为标准答案不准

**关键发现**：
- 评测标准本身也要迭代，不能迷信自动算出来的ground truth
- 大模型打分太宽松会导致区分度不够，需要加分数区间约束
- 人工标注标准答案是最准确的评测方式

---

## P2阶段：RAG语义检索层（待做）
