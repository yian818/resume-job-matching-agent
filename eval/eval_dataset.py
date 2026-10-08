"""
eval_dataset.py - 简历-岗位匹配 Agent 测试集

包含：
  - 50 份简历（真实感强的文本 + 标准答案）
  - 20 个 JD（真实岗位描述 + 标准答案）

用法：
    from eval_dataset import RESUMES, JOBS
    # 遍历
    for r in RESUMES:
        print(r["resume_text"])
"""

RESUMES = [
    {
        "resume_id": "R001",
        "resume_text": """张明，男，28岁。
学历：北京大学，计算机科学，硕士，2020年毕业。
工作经历：
- 2020-2023 字节跳动 算法工程师，负责推荐系统优化，使用 Python、PyTorch、Transformer，上线后CTR提升12%。
- 2023-至今 阿里云 高级算法工程师，负责LLM应用开发，精通LangGraph、RAG、向量数据库（Milvus）、Prompt Engineering。
技能：Python, PyTorch, LangGraph, RAG, Milvus, LLM, Prompt Engineering, 大模型微调, Docker, Kubernetes。
项目：独立完成一个基于LangGraph的AI客服Agent，支持多轮对话和工具调用，日均处理5000+请求。""",
        "expected_resume": {"name": "张明", "education": "硕士", "work_year": "5年", "skills": ["Python", "PyTorch", "LangGraph", "RAG", "Milvus", "LLM", "Prompt Engineering"], "has_llm_project": True}
    },
    {
        "resume_id": "R002",
        "resume_text": """李婷，女，25岁。
学历：浙江大学，软件工程，本科，2023年毕业。
工作经历：
- 2023-至今 蚂蚁集团 后端开发工程师，负责支付系统，技术栈：Java, Spring Boot, MySQL, Redis, Kafka。
项目：参与微服务架构改造，将单体服务拆分为12个微服务，接口响应时间降低40%。""",
        "expected_resume": {"name": "李婷", "education": "本科", "work_year": "2年", "skills": ["Java", "Spring Boot", "MySQL", "Redis", "Kafka"], "has_llm_project": False}
    },
    {
        "resume_id": "R003",
        "resume_text": """王强，男，30岁。
学历：华中科技大学，自动化，本科，2016年毕业。
工作经历：
- 2016-2019 华为 嵌入式工程师，负责IoT设备开发，C++、Python、RTOS。
- 2019-2022 小鹏汽车 自动驾驶算法工程师，使用Python、PyTorch、CUDA进行感知模型训练。
- 2022-至今 地平线 高级算法工程师，负责车端视觉模型部署优化，精通TensorRT、ONNX、模型压缩。
技能：Python, C++, PyTorch, CUDA, TensorRT, ONNX, 计算机视觉, 边缘计算。
项目：主导一个YOLOv8车端部署项目，推理速度提升3倍，在Jetson Orin上达到30FPS。""",
        "expected_resume": {"name": "王强", "education": "本科", "work_year": "8年", "skills": ["Python", "C++", "PyTorch", "CUDA", "TensorRT", "ONNX"], "has_llm_project": False}
    },
    {
        "resume_id": "R004",
        "resume_text": """陈晓，女，26岁。
学历：复旦大学，金融学，本科，2022年毕业。
工作经历：
- 2022-至今 平安科技 金融产品经理，负责信贷审批系统产品规划，擅长数据分析（SQL、Python）和AIGC应用落地。
- 参与公司AI助手项目，使用LangChain+LLM实现智能问答。
技能：产品管理, SQL, Python, LangChain, LLM应用, 数据分析。
项目：主导一个智能风控助手，集成LLM生成分析报告，审批效率提升60%。""",
        "expected_resume": {"name": "陈晓", "education": "本科", "work_year": "3年", "skills": ["SQL", "Python", "LangChain", "LLM"], "has_llm_project": True}
    },
    {
        "resume_id": "R005",
        "resume_text": """赵磊，男，27岁。
学历：南京大学，数学与应用数学，本科，2021年毕业。
工作经历：
- 2021-2023 腾讯 数据分析师，负责游戏业务数据分析，使用Python、SQL、Tableau，输出30+份分析报告。
- 2023-至今 快手 高级数据分析师，负责推荐策略效果评估，搭建AB实验平台。
技能：Python, SQL, Tableu, AB测试, 统计分析, 机器学习。""",
        "expected_resume": {"name": "赵磊", "education": "本科", "work_year": "4年", "skills": ["Python", "SQL", "Tableau", "AB Testing", "Statistics"], "has_llm_project": False}
    },
    {
        "resume_id": "R006",
        "resume_text": """刘芳，女，24岁。
学历：同济大学，设计学，本科，2024年毕业。
工作经历：
- 2024-至今 字节跳动 UX设计师，负责抖音创作者平台设计，使用Figma、Principle。
项目：设计一套AI辅助创作工具界面，用户满意度提升25%。""",
        "expected_resume": {"name": "刘芳", "education": "本科", "work_year": "1年", "skills": ["Figma", "Principle", "UX Design", "UI Design"], "has_llm_project": False}
    },
    {
        "resume_id": "R007",
        "resume_text": """孙伟，男，29岁。
学历：上海交通大学，电子信息，硕士，2019年毕业。
工作经历：
- 2019-2021 商汤科技 计算机视觉工程师，负责人脸检测模型研发。
- 2021-2024 百度 高级视觉算法工程师，负责视频理解，使用PyTorch、CUDA、MMSync。
- 2024-至今 字节跳动 视觉大模型算法专家，负责Video-LLM预训练和微调。
技能：PyTorch, CUDA, Python, C++, 计算机视觉, Video-LLM, 大模型预训练, 分布式训练。
项目：主导一个Video-LLM基座模型，在Video-MME基准上达到SOTA。""",
        "expected_resume": {"name": "孙伟", "education": "硕士", "work_year": "6年", "skills": ["PyTorch", "CUDA", "Python", "C++", "Video-LLM"], "has_llm_project": True}
    },
    {
        "resume_id": "R008",
        "resume_text": """周敏，女，26岁。
学历：武汉大学，法学，本科，2021年毕业。
工作经历：
- 2021-2023 金杜律师事务所 律师，专注知识产权诉讼。
- 2023-至今 字节跳动 法务专员，负责AI相关合规审查，熟悉《生成式AI管理办法》。
技能：法律合规, 知识产权, 合同审核, Python(基础)。""",
        "expected_resume": {"name": "周敏", "education": "本科", "work_year": "4年", "skills": ["Legal Compliance", "IP Law"], "has_llm_project": False}
    },
    {
        "resume_id": "R009",
        "resume_text": """吴刚，男，31岁。
学历：清华大学，计算机，博士，2018年毕业。
工作经历：
- 2018-2020 微软亚洲研究院 研究员，发表ACL/EMNLP论文5篇，研究方向：NLP、对话系统。
- 2020-2023 OpenAI 研究员，参与GPT系列模型训练，专注于RLHF和安全对齐。
- 2023-至今 智谱AI 首席科学家，负责GLM系列模型研发。
技能：Python, PyTorch, NLP, RLHF, Transformer, 分布式训练, 大模型安全。
项目：提出一种新的RLHF变体算法，已应用于GLM-4，训练成本降低20%。""",
        "expected_resume": {"name": "吴刚", "education": "博士", "work_year": "7年", "skills": ["Python", "PyTorch", "NLP", "RLHF", "Transformer"], "has_llm_project": True}
    },
    {
        "resume_id": "R010",
        "resume_text": """郑华，男，25岁。
学历：西安交通大学，通信工程，本科，2023年毕业。
工作经历：
- 2023-至今 中国移动 网络运维工程师，负责5G基站维护，使用Python做自动化脚本。
技能：Python(脚本), Shell, Linux, 5G, SNMP。""",
        "expected_resume": {"name": "郑华", "education": "本科", "work_year": "2年", "skills": ["Python", "Shell", "Linux"], "has_llm_project": False}
    },
    {
        "resume_id": "R011",
        "resume_text": """黄丽，女，27岁。
学历：中山大学，会计学，本科，2020年毕业。
工作经历：
- 2020-2022 德勤 审计师，负责上市公司年报审计。
- 2022-至今 腾讯 财务分析师，负责游戏业务财务建模，使用Excel、Python（pandas）、SQL。
项目：搭建一个自动化报表工具，每月节省40工时。""",
        "expected_resume": {"name": "黄丽", "education": "本科", "work_year": "5年", "skills": ["Excel", "Python", "SQL", "财务分析", "财务建模"], "has_llm_project": False}
    },
    {
        "resume_id": "R012",
        "resume_text": """杨帆，男，26岁。
学历：哈尔滨工业大学，机器人工程，硕士，2022年毕业。
工作经历：
- 2022-至今 大疆创新 机器人算法工程师，负责无人机路径规划，使用Python、C++、ROS、Gazebo。
技能：Python, C++, ROS, SLAM, 路径规划, Gazebo, PyTorch。
项目：设计一个动态避障算法，在复杂环境下的成功率达98%。""",
        "expected_resume": {"name": "杨帆", "education": "硕士", "work_year": "3年", "skills": ["Python", "C++", "ROS", "SLAM"], "has_llm_project": False}
    },
    {
        "resume_id": "R013",
        "resume_text": """林燕，女，28岁。
学历：四川大学，汉语言文学，本科，2018年毕业。
工作经历：
- 2018-2020 人民日报 编辑，负责新闻稿件撰写与审核。
- 2020-至今 字节跳动 内容策略产品经理，负责短视频内容生态，擅长用数据驱动决策。
技能：内容运营, 产品管理, SQL, Python(数据分析), AIGC内容生成。
项目：主导AI内容审核策略升级，误判率从5%降至0.5%。""",
        "expected_resume": {"name": "林燕", "education": "本科", "work_year": "7年", "skills": ["Product Management", "SQL", "Python", "Content Strategy"], "has_llm_project": True}
    },
    {
        "resume_id": "R014",
        "resume_text": """徐杰，男，30岁。
学历：电子科技大学，微电子，硕士，2016年毕业。
工作经历：
- 2016-2019 海康威视 IC设计工程师，负责模拟电路设计。
- 2019-2022 华为海思 高级IC设计师，负责5G基带芯片模拟前端。
- 2022-至今 地平线 芯片架构师，负责新一代AI芯片架构设计。
技能：Verilog, SystemVerilog, 模拟IC设计, 芯片架构, Python, C。""",
        "expected_resume": {"name": "徐杰", "education": "硕士", "work_year": "9年", "skills": ["Verilog", "IC Design", "Chip Architecture"], "has_llm_project": False}
    },
    {
        "resume_id": "R015",
        "resume_text": """马红，女，24岁。
学历：北京语言大学，英语，本科，2024年毕业。
工作经历：
- 2024-至今 携程 海外运营专员，负责东南亚市场运营，使用Python做数据分析。
技能：英语(CET-6), Python, SQL, 数据分析, 跨境电商运营。""",
        "expected_resume": {"name": "马红", "education": "本科", "work_year": "1年", "skills": ["English", "Python", "SQL"], "has_llm_project": False}
    },
    {
        "resume_id": "R016",
        "resume_text": """胡强，男，32岁。
学历：中国科学院大学，物理学，博士，2015年毕业。
工作经历：
- 2015-2018 阿里云计算 量子计算研究员，发表Nature子刊论文2篇。
- 2018-2021 IBM 研究员，专注量子纠错。
- 2021-至今 本源量子 首席科学家，负责量子编译器研发。
技能：Python, Qiskit, 量子计算, 理论物理, 算法设计。
项目：开发一个量子电路优化工具，编译效率提升10倍。""",
        "expected_resume": {"name": "胡强", "education": "博士", "work_year": "10年", "skills": ["Python", "Qiskit", "Quantum Computing"], "has_llm_project": False}
    },
    {
        "resume_id": "R017",
        "resume_text": """宋佳，女，25岁。
学历：中国传媒大学，数字媒体艺术，本科，2023年毕业。
工作经历：
- 2023-至今 哔哩哔哩 视频特效师，使用AE、PR、Blender。
项目：制作《原神》官方二创视频，播放量超500万。
技能：After Effects, Premiere, Blender, C4D, 视频剪辑。""",
        "expected_resume": {"name": "宋佳", "education": "本科", "work_year": "2年", "skills": ["AE", "PR", "Blender", "C4D"], "has_llm_project": False}
    },
    {
        "resume_id": "R018",
        "resume_text": """何伟，男，29岁。
学历：天津大学，土木工程，本科，2017年毕业。
工作经历：
- 2017-2020 中建三局 结构工程师，负责高层建筑设计。
- 2020-至今 碧桂园 项目总工，管理10+人团队。
技能：AutoCAD, Revit, PKPM, 结构设计, 项目管理。""",
        "expected_resume": {"name": "何伟", "education": "本科", "work_year": "8年", "skills": ["AutoCAD", "Revit", "PKPM"], "has_llm_project": False}
    },
    {
        "resume_id": "R019",
        "resume_text": """曹雪，女，26岁。
学历：东南大学，生物医学工程，硕士，2022年毕业。
工作经历：
- 2022-至今 联影医疗 算法工程师，负责医学影像AI辅助诊断，使用Python、PyTorch、MONAI。
技能：Python, PyTorch, MONAI, 医学影像分析, U-Net, 3D CNN。
项目：开发肺结节检测模型，在LIDC-IDRI数据集上F1达0.92。""",
        "expected_resume": {"name": "曹雪", "education": "硕士", "work_year": "3年", "skills": ["Python", "PyTorch", "MONAI", "Medical Imaging"], "has_llm_project": True}
    },
    {
        "resume_id": "R020",
        "resume_text": """邓明，男，27岁。
学历：北京航空航天大学，飞行器设计，硕士，2021年毕业。
工作经历：
- 2021-2023 航天科技集团 气动工程师，负责飞行器外形优化。
- 2023-至今 商业航天公司 结构设计师，使用ANSYS、CATIA。
技能：ANSYS, CATIA, Python, 流体力学, 结构设计。""",
        "expected_resume": {"name": "邓明", "education": "硕士", "work_year": "4年", "skills": ["ANSYS", "CATIA", "Python"], "has_llm_project": False}
    },
    {
        "resume_id": "R021",
        "resume_text": """田静，女，30岁。
学历：对外经济贸易大学，国际贸易，本科，2017年毕业。
工作经历：
- 2017-2019 沃尔玛 采购专员，负责消费品进口。
- 2019-至今 拼多多 国际业务运营，负责东南亚市场选品和供应链管理。
技能：跨境电商, 供应链管理, 数据分析, 英语(流利)。""",
        "expected_resume": {"name": "田静", "education": "本科", "work_year": "8年", "skills": ["Cross-border E-commerce", "Supply Chain", "English"], "has_llm_project": False}
    },
    {
        "resume_id": "R022",
        "resume_text": """韩冰，男，28岁。
学历：山东大学，计算机科学，硕士，2020年毕业。
工作经历：
- 2020-2022 美团 搜索算法工程师，负责外卖搜索排序，使用TensorFlow、Redis、Flink。
- 2022-至今 滴滴 高级推荐算法工程师，负责打车需求预测，精通深度学习、时空序列预测。
技能：Python, TensorFlow, PyTorch, Flink, Redis, 推荐系统, 时空预测。
项目：开发一个实时需求预测系统，预测准确率提升15%，日均节省运力10万单。""",
        "expected_resume": {"name": "韩冰", "education": "硕士", "work_year": "5年", "skills": ["Python", "TensorFlow", "PyTorch", "Flink", "Recommendation System"], "has_llm_project": True}
    },
    {
        "resume_id": "R023",
        "resume_text": """冯瑶，女，25岁。
学历：南京艺术学院，视觉传达，本科，2024年毕业。
工作经历：
- 2024-至今 阿里巴巴 品牌设计师，负责淘宝双11视觉设计。
技能：PS, AI, C4D, 品牌设计。""",
        "expected_resume": {"name": "冯瑶", "education": "本科", "work_year": "1年", "skills": ["Photoshop", "Illustrator", "C4D"], "has_llm_project": False}
    },
    {
        "resume_id": "R024",
        "resume_text": """蒋涛，男，33岁。
学历：浙江大学，控制科学与工程，博士，2014年毕业。
工作经历：
- 2014-2017 波士顿动力 机器人控制算法工程师。
- 2017-2020 特斯拉 AI工程师，负责Autopilot感知。
- 2020-至今 蔚来自助驾驶总监，管理50人团队。
技能：C++, Python, ROS, 深度学习, 自动驾驶, 团队管理。
项目：主导第三代自动驾驶系统研发，完成10万+公里路测。""",
        "expected_resume": {"name": "蒋涛", "education": "博士", "work_year": "11年", "skills": ["C++", "Python", "ROS", "Autonomous Driving"], "has_llm_project": True}
    },
    {
        "resume_id": "R025",
        "resume_text": """沈怡，女，26岁。
学历：中央财经大学，财务管理，本科，2021年毕业。
工作经历：
- 2021-至今 中金公司 行业研究员，覆盖TMT赛道，撰写深度报告50+篇。
技能：Financial Modeling, Python, SQL, 行业研究, Wind。""",
        "expected_resume": {"name": "沈怡", "education": "本科", "work_year": "4年", "skills": ["Financial Modeling", "Python", "SQL", "Industry Research"], "has_llm_project": False}
    },
    {
        "resume_id": "R026",
        "resume_text": """袁磊，男，27岁。
学历：北京邮电大学，通信工程，本科，2020年毕业。
工作经历：
- 2020-2022 中兴通讯 5G协议栈开发，C语言。
- 2022-至今 华为 高级协议开发工程师，负责5G-A标准制定。
技能：C, C++, 5G协议, 通信原理, Linux。""",
        "expected_resume": {"name": "袁磊", "education": "本科", "work_year": "5年", "skills": ["C", "C++", "5G Protocol"], "has_llm_project": False}
    },
    {
        "resume_id": "R027",
        "resume_text": """许梅，女，29岁。
学历：江南大学，食品科学，硕士，2018年毕业。
工作经历：
- 2018-2021 伊利集团 研发工程师，负责奶粉配方研发。
- 2021-至今 蒙牛 高级研发经理，管理15人团队。
技能：食品化学, 配方研发, HPLC, GC-MS, 团队管理。""",
        "expected_resume": {"name": "许梅", "education": "硕士", "work_year": "7年", "skills": ["Food Science", "R&D", "HPLC"], "has_llm_project": False}
    },
    {
        "resume_id": "R028",
        "resume_text": """程鹏，男，25岁。
学历：四川大学，心理学，本科，2023年毕业。
工作经历：
- 2023-至今 网易 用户体验研究员，负责游戏用户研究，使用问卷、访谈、眼动实验。
技能：SPSS, Python, 用户研究, 实验设计。""",
        "expected_resume": {"name": "程鹏", "education": "本科", "work_year": "2年", "skills": ["Python", "SPSS", "User Research"], "has_llm_project": False}
    },
    {
        "resume_id": "R029",
        "resume_text": """苏晴，女，28岁。
学历：同济大学，德语，本科，2019年毕业。
工作经历：
- 2019-2021 宝马中国 翻译，负责技术文档翻译。
- 2021-至今 大众汽车 项目经理，负责中德合作项目。
技能：德语(母语级), 英语, 项目管理, 跨文化沟通。""",
        "expected_resume": {"name": "苏晴", "education": "本科", "work_year": "6年", "skills": ["German", "English", "Project Management"], "has_llm_project": False}
    },
    {
        "resume_id": "R030",
        "resume_text": """梁博，男，31岁。
学历：中国科学技术大学，核工程，博士，2017年毕业。
工作经历：
- 2017-2020 中广核 核反应堆仿真工程师。
- 2020-至今 私营航天 热防护系统专家。
技能：ANSYS, FLUENT, Python, 热力学, 有限元分析。""",
        "expected_resume": {"name": "梁博", "education": "博士", "work_year": "8年", "skills": ["ANSYS", "FLUENT", "Python"], "has_llm_project": False}
    },
    {
        "resume_id": "R031",
        "resume_text": """夏雨，女，24岁。
学历：华东师范大学，教育学，本科，2024年毕业。
工作经历：
- 2024-至今 猿辅导 教研老师，负责高中数学课程开发。
技能：数学, 课程设计, Python(基础)。""",
        "expected_resume": {"name": "夏雨", "education": "本科", "work_year": "1年", "skills": ["Education", "Curriculum Design"], "has_llm_project": False}
    },
    {
        "resume_id": "R032",
        "resume_text": """唐杰，男，30岁。
学历：华中科技大学，机械工程，硕士，2017年毕业。
工作经历：
- 2017-2020 三一重工 液压工程师，负责挖掘机液压系统设计。
- 2020-至今 徐工集团 液压系统总工，带领团队完成10+型号液压系统设计。
技能：Hydraulic System, SolidWorks, ANSYS, C++, 项目管理。""",
        "expected_resume": {"name": "唐杰", "education": "硕士", "work_year": "8年", "skills": ["Hydraulic System", "SolidWorks", "ANSYS"], "has_llm_project": False}
    },
    {
        "resume_id": "R033",
        "resume_text": """叶丽，女，27岁。
学历：深圳大学，广告学，本科，2020年毕业。
工作经历：
- 2020-2022 奥美广告 创意文案，服务多个国际品牌。
- 2022-至今 分众传媒 内容策划总监，管理20人团队。
技能：创意文案, 品牌策划, PS, 项目管理。""",
        "expected_resume": {"name": "叶丽", "education": "本科", "work_year": "5年", "skills": ["Copywriting", "Brand Strategy", "Project Management"], "has_llm_project": False}
    },
    {
        "resume_id": "R034",
        "resume_text": """魏强，男，26岁。
学历：西北工业大学，航海技术，本科，2021年毕业。
工作经历：
- 2021-2023 招商局 远洋船长，负责远洋货轮航行。
- 2023-至今 中远海运 船队调度主管。
技能：航海技术, GMDSS, 船舶管理, 英语。""",
        "expected_resume": {"name": "魏强", "education": "本科", "work_year": "4年", "skills": ["Maritime Navigation", "English"], "has_llm_project": False}
    },
    {
        "resume_id": "R035",
        "resume_text": """金梅，女，32岁。
学历：北京协和医学院，临床医学，博士，2015年毕业。
工作经历：
- 2015-2018 北京协和医院 住院医师，内分泌科。
- 2018-2022 梅奥诊所（访问学者） 内分泌研究。
- 2022-至今 平安好医生 首席医学官，负责AI问诊产品医学审核。
技能：临床医学, 内分泌, AI医疗, 产品管理。
项目：主导AI糖尿病管理助手，服务100万+患者，获国家药监局三类医疗器械认证。""",
        "expected_resume": {"name": "金梅", "education": "博士", "work_year": "10年", "skills": ["Clinical Medicine", "Endocrinology", "AI Healthcare"], "has_llm_project": True}
    },
    {
        "resume_id": "R036",
        "resume_text": """董勇，男·29岁。
学历：大连海事大学，轮机工程，本科，2018年毕业。
工作经历：
- 2018-2021 地中海航运 轮机长。
- 2021-至今 马士基 船舶技术经理。
技能：轮机工程, 英语, 船舶维修, 安全管理。""",
        "expected_resume": {"name": "董勇", "education": "本科", "work_year": "7年", "skills": ["Marine Engineering", "English"], "has_llm_project": False}
    },
    {
        "resume_id": "R037",
        "resume_text": """白洁，女，25岁。
学历：中央美术学院，油画，本科，2023年毕业。
工作经历：
- 2023-至今 独立插画师，接商单和版权授权。
项目：个人IP"小白的日常"全网粉丝50万，与喜茶、元气森林合作联名。
技能：Procreate, PS, SAI, 插画设计。""",
        "expected_resume": {"name": "白洁", "education": "本科", "work_year": "2年", "skills": ["Procreate", "Photoshop", "Illustration"], "has_llm_project": False}
    },
    {
        "resume_id": "R038",
        "resume_text": """罗鑫，男，28岁。
学历：西南财经大学，金融学，硕士，2020年毕业。
工作经历：
- 2020-2022 华夏基金 研究员，覆盖新能源赛道。
- 2022-至今 高瓴资本 投资经理，负责成长期项目尽调。
技能：Financial Modeling, Python, SQL, 行业研究, 尽职调查。""",
        "expected_resume": {"name": "罗鑫", "education": "硕士", "work_year": "5年", "skills": ["Financial Modeling", "Python", "SQL", "Investment"], "has_llm_project": False}
    },
    {
        "resume_id": "R039",
        "resume_text": """谢燕，女，26岁。
学历：湖南大学，服装设计与工程，本科，2022年毕业。
工作经历：
- 2022-至今 安踏 面料开发工程师，负责运动功能性面料研发。
技能：纺织材料, CAD, 面料检测, Python(数据分析)。""",
        "expected_resume": {"name": "谢燕", "education": "本科", "work_year": "3年", "skills": ["Textile Materials", "CAD", "Python"], "has_llm_project": False}
    },
    {
        "resume_id": "R040",
        "resume_text": """蔡明，男，30岁。
学历：浙江大学，光电器件，博士，2017年毕业。
工作经历：
- 2017-2020 京东方 显示技术研究员，负责OLED材料开发。
- 2020-至今 TCL华星 光电技术总监，管理30人研发团队。
技能：OLED, 有机材料, PLDT, 光谱分析, 团队管理。""",
        "expected_resume": {"name": "蔡明", "education": "博士", "work_year": "8年", "skills": ["OLED", "Organic Materials", "Spectroscopy"], "has_llm_project": False}
    },
    {
        "resume_id": "R041",
        "resume_text": """贾玲，女，24岁。
学历：北京电影学院，表演，本科，2024年毕业。
工作经历：
- 2024-至今 自由演员，参演网剧《春风十里》。
技能：表演, 台词, 舞蹈。""",
        "expected_resume": {"name": "贾玲", "education": "本科", "work_year": "1年", "skills": ["Acting", "Performance"], "has_llm_project": False}
    },
    {
        "resume_id": "R042",
        "resume_text": """龚伟，男，33岁。
学历：东南大学，交通工程，硕士，2014年毕业。
工作经历：
- 2014-2018 交通运输部规划设计院 工程师，负责城市交通规划。
- 2018-至今 高德地图 交通大脑产品负责人，负责城市级交通治理方案。
技能：交通规划, Python, SQL, Product Management, 数据分析。
项目：主导杭州市交通大脑2.0，拥堵指数下降18%，获交通运输部科技进步奖。""",
        "expected_resume": {"name": "龚伟", "education": "硕士", "work_year": "11年", "skills": ["Transportation Planning", "Python", "SQL", "Product Management"], "has_llm_project": True}
    },
    {
        "resume_id": "R043",
        "resume_text": """潘丽，女，27岁。
学历：南京师范大学，英语教育，本科，2020年毕业。
工作经历：
- 2020-2022 学而思 英语教学主管，管理15人教师团队。
- 2022-至今 新东方在线 课程研发总监，负责英语课程体系重构。
技能：英语(专八), 课程设计, 团队管理, 线上教学。""",
        "expected_resume": {"name": "潘丽", "education": "本科", "work_year": "5年", "skills": ["English", "Curriculum Design", "Team Management"], "has_llm_project": False}
    },
    {
        "resume_id": "R044",
        "resume_text": """段飞，男，29岁。
学历：重庆大学，给排水科学与工程，本科，2018年毕业。
工作经历：
- 2018-2021 中建市政 给排水设计师，负责城市管网设计。
- 2021-至今 苏伊士环境 水务技术经理，负责污水处理项目。
技能：AutoCAD, WaterCAD, 给排水, 项目管理。""",
        "expected_resume": {"name": "段飞", "education": "本科", "work_year": "7年", "skills": ["AutoCAD", "WaterCAD", "Project Management"], "has_llm_project": False}
    },
    {
        "resume_id": "R045",
        "resume_text": """范雨，女，25岁。
学历：中国农业大学，动物医学，本科，2023年毕业。
工作经历：
- 2023-至今 瑞鹏宠物医院 主治兽医，擅长犬猫外科。
技能：兽医临床, 外科手术, 放射影像。""",
        "expected_resume": {"name": "范雨", "education": "本科", "work_year": "2年", "skills": ["Veterinary Medicine", "Surgery"], "has_llm_project": False}
    },
    {
        "resume_id": "R046",
        "resume_text": """秦风，男，31岁。
学历：武汉大学，历史学，博士，2017年毕业。
工作经历：
- 2017-2020 湖北省博物馆 研究馆员，负责青铜器修复。
- 2020-至今 故宫博物院 古陶瓷修复专家。
项目：主持国家文物局科研项目，完成唐三彩修复100余件。
技能：文物保护, 陶瓷修复, 考古学, Python(基础)。""",
        "expected_resume": {"name": "秦风", "education": "博士", "work_year": "8年", "skills": ["Cultural Heritage Conservation", "Ceramics"], "has_llm_project": True}
    },
    {
        "resume_id": "R047",
        "resume_text": """姜宁，女，26岁。
学历：上海财经大学，资产评估，本科，2021年毕业。
工作经历：
- 2021-至今 中联资产评估 资产评估师，负责企业并购估值。
技能：资产评估, Excel, Python, 会计。""",
        "expected_resume": {"name": "姜宁", "education": "本科", "work_year": "4年", "skills": ["Asset Valuation", "Excel", "Python"], "has_llm_project": False}
    },
    {
        "resume_id": "R048",
        "resume_text": """钟亮，男，28岁。
学历：湖南大学，土木工程，硕士，2020年毕业。
工作经历：
- 2020-2023 中铁隧道局 隧道工程师，参与深埋隧道施工。
- 2023-至今 中交隧道工程 技术负责人，负责盾构施工技术管理。
技能：隧道工程,盾构机, Python, CAD, 项目管理。
项目：主导一条8km地铁隧道施工，提前2个月竣工。""",
        "expected_resume": {"name": "钟亮", "education": "硕士", "work_year": "5年", "skills": ["Tunnel Engineering", "Shield Machine", "Python", "CAD"], "has_llm_project": True}
    },
    {
        "resume_id": "R049",
        "resume_text": """雷晓，女，24岁。
学历：苏州大学，纳米科技，本科，2024年毕业。
工作经历：
- 2024-至今 中科院苏州纳米所 科研助理，负责二维材料合成。
技能：SEM, XRD, 纳米材料, Python(数据处理)。""",
        "expected_resume": {"name": "雷晓", "education": "本科", "work_year": "1年", "skills": ["Nanomaterials", "SEM", "XRD", "Python"], "has_llm_project": False}
    },
    {
        "resume_id": "R050",
        "resume_text": """卢斌，男，32岁。
学历：西安电子科技大学，信息安全，博士，2016年毕业。
工作经历：
- 2016-2019 奇安信 安全研究员，负责漏洞挖掘。
- 2019-2022 字节跳动 安全架构师，负责核心系统安全。
- 2022-至今 阿里安全 首席安全专家，负责AI安全治理。
技能：Python, Go, 渗透测试, AI安全, 安全架构, LLM安全。
项目：构建企业级AI安全扫描平台，拦截99.7%的Prompt注入攻击。""",
        "expected_resume": {"name": "卢斌", "education": "博士", "work_year": "9年", "skills": ["Python", "Go", "Penetration Testing", "AI Security", "LLM Security"], "has_llm_project": True}
    },
]

JOBS = [
    {
        "jd_id": "J001",
        "jd_text": "AI Agent工程师（大厂核心部门）\n地点：北京/上海\n经验：3年以上\n要求：\n- 精通Python，有LangGraph/AutoGen等框架实战经验\n- 熟悉LLM微调、RAG、向量数据库\n- 有独立Agent产品落地经验\n- 加分项：有开源项目或顶会论文",
        "expected": {"should_recommend": True, "reason": "候选人与岗位核心技能高度匹配"},
        "key_skills": ["Python", "LangGraph", "RAG", "LLM"],
        "required_years": 3,
        "education": "本科"
    },
    {
        "jd_id": "J002",
        "jd_text": "后端开发工程师（金融方向）\n地点：上海\n经验：2年以上\n要求：\n- 精通Java/Spring Boot\n- 熟悉MySQL、Redis、消息队列\n- 有分布式系统设计经验",
        "expected": {"should_recommend": True, "reason": "候选人技能与岗位高度匹配"},
        "key_skills": ["Java", "Spring Boot", "MySQL", "Redis"],
        "required_years": 2,
        "education": "本科"
    },
    {
        "jd_id": "J003",
        "jd_text": "计算机视觉算法工程师\n地点：深圳\n经验：2年以上\n要求：\n- 精通PyTorch\n- 熟悉目标检测、图像分割\n- 有模型部署优化经验（TensorRT/ONNX）\n- 硕士优先",
        "expected": {"should_recommend": True, "reason": "候选人在CV领域有深厚积累"},
        "key_skills": ["PyTorch", "Computer Vision", "TensorRT", "CUDA"],
        "required_years": 2,
        "education": "硕士"
    },
    {
        "jd_id": "J004",
        "jd_text": "数据分析师（电商方向）\n地点：杭州\n经验：1-3年\n要求：\n- 精通SQL和Python\n- 熟练使用Tableau/Power BI\n- 有AB测试经验\n- 对数据敏感，逻辑清晰",
        "expected": {"should_recommend": True, "reason": "候选人数据分析和AB测试经验丰富"},
        "key_skills": ["SQL", "Python", "Tableau", "AB Testing"],
        "required_years": 2,
        "education": "本科"
    },
    {
        "jd_id": "J005",
        "jd_text": "大模型算法工程师\n地点：北京\n经验：5年以上\n要求：\n- 顶会论文（NeurIPS/ICML/ACL）优先\n- 精通RLHF、模型对齐\n- 有大规模分布式训练经验\n- 博士优先",
        "expected": {"should_recommend": True, "reason": "候选人是大模型安全领域的顶尖专家"},
        "key_skills": ["RLHF", "Transformer", "分布式训练", "Python"],
        "required_years": 5,
        "education": "博士"
    },
    {
        "jd_id": "J006",
        "jd_text": "产品运营专员\n地点：广州\n经验：1年以下\n要求：\n- 本科，市场营销相关专业\n- 有互联网实习经历\n- 熟练使用Office\n- 沟通能力强",
        "expected": {"should_recommend": False, "reason": "岗位要求较低，需具体看简历匹配度"},
        "key_skills": ["运营", "Excel", "沟通"],
        "required_years": 1,
        "education": "本科"
    },
    {
        "jd_id": "J007",
        "jd_text": "AI产品经理\n地点：北京\n经验：2年以上\n要求：\n- 有AI产品从0到1经验\n- 懂技术，能与算法团队顺畅沟通\n- 熟悉Prompt Engineering、RAG原理\n- 有较强的数据分析能力",
        "expected": {"should_recommend": True, "reason": "候选人既懂技术又有产品经验"},
        "key_skills": ["AI Product", "Prompt Engineering", "Data Analysis"],
        "required_years": 2,
        "education": "本科"
    },
    {
        "jd_id": "J008",
        "jd_text": "嵌入式软件工程师（汽车电子）\n地点：上海\n经验：3年以上\n要求：\n- 精通C/C++\n- 熟悉AUTOSAR、CAN总线\n- 有车载系统开发经验\n- 本科及以上学历",
        "expected": {"should_recommend": False, "reason": "候选人虽有嵌入式经验但非汽车电子方向"},
        "key_skills": ["C", "C++", "AUTOSAR", "CAN"],
        "required_years": 3,
        "education": "本科"
    },
    {
        "jd_id": "J009",
        "jd_text": "NLP算法工程师\n地点：北京\n经验：2年以上\n要求：\n- 精通Python、PyTorch\n- 熟悉Transformer、BERT、GPT\n- 有LLM应用开发经验\n- 顶会论文优先",
        "expected": {"should_recommend": True, "reason": "候选人NLP方向深耕多年"},
        "key_skills": ["Python", "PyTorch", "NLP", "Transformer"],
        "required_years": 2,
        "education": "硕士"
    },
    {
        "jd_id": "J010",
        "jd_text": "机械结构工程师\n地点：东莞\n经验：3年以上\n要求：\n- 精通SolidWorks、ANSYS\n- 有消费电子结构设计经验\n- 熟悉模具工艺\n- 本科及以上学历",
        "expected": {"should_recommend": False, "reason": "候选人结构方向与岗位不完全匹配"},
        "key_skills": ["SolidWorks", "ANSYS", "Mechanical Design"],
        "required_years": 3,
        "education": "本科"
    },
    {
        "jd_id": "J011",
        "jd_text": "量化交易研究员\n地点：上海\n经验：3年以上\n要求：\n- 数学/物理/金融工程背景\n- 精通Python、C++\n- 有量化策略开发经验\n- 熟悉时序预测、强化学习\n- 硕士及以上",
        "expected": {"should_recommend": True, "reason": "候选人量化投研背景与岗位要求契合"},
        "key_skills": ["Python", "C++", "Quantitative Trading", "Time Series"],
        "required_years": 3,
        "education": "硕士"
    },
    {
        "jd_id": "J012",
        "jd_text": "Flutter移动端开发工程师\n地点：深圳\n经验：2年以上\n要求：\n- 精通Dart、Flutter\n- 熟悉iOS/Android原生开发\n- 有完整App上架经验\n- 本科及以上学历",
        "expected": {"should_recommend": False, "reason": "候选人技能与岗位要求不匹配"},
        "key_skills": ["Flutter", "Dart", "iOS", "Android"],
        "required_years": 2,
        "education": "本科"
    },
    {
        "jd_id": "J013",
        "jd_text": "AI安全研究员\n地点：北京\n经验：2年以上\n要求：\n- 精通Python/Go\n- 熟悉LLM安全、Prompt注入检测\n- 有渗透测试经验\n- 有Top安全会议（USENIX Security/CCS）论文优先",
        "expected": {"should_recommend": True, "reason": "候选人正是AI安全方向顶级专家"},
        "key_skills": ["Python", "LLM Security", "Penetration Testing", "Go"],
        "required_years": 2,
        "education": "博士"
    },
    {
        "jd_id": "J014",
        "jd_text": "外贸业务员\n地点：宁波\n经验：1年以上\n要求：\n- 英语CET-6\n- 有B2B外贸经验\n- 熟悉阿里巴巴国际站\n- 本科及以上学历",
        "expected": {"should_recommend": False, "reason": "候选人方向不符"},
        "key_skills": ["English", "Cross-border Trade", "B2B"],
        "required_years": 1,
        "education": "本科"
    },
    {
        "jd_id": "J015",
        "jd_text": "自动驾驶感知算法工程师\n地点：北京\n经验：3年以上\n要求：\n- 精通C++/Python\n- 熟悉视觉/激光雷达融合感知\n- 有量产项目经验\n- 硕士及以上",
        "expected": {"should_recommend": True, "reason": "候选人自动驾驶领域资深专家"},
        "key_skills": ["C++", "Python", "Perception", "Sensor Fusion"],
        "required_years": 3,
        "education": "硕士"
    },
    {
        "jd_id": "J016",
        "jd_text": "人力资源BP\n地点：北京\n经验：3年以上\n要求：\n- 有互联网公司HRBP经验\n- 熟悉招聘、员工关系、绩效管理\n- 良好的沟通能力\n- 本科及以上学历",
        "expected": {"should_recommend": False, "reason": "岗位方向完全不同"},
        "key_skills": ["HR", "Recruiting", "Employee Relations"],
        "required_years": 3,
        "education": "本科"
    },
    {
        "jd_id": "J017",
        "jd_text": "视频算法工程师（AIGC方向）\n地点：杭州\n经验：2年以上\n要求：\n- 精通Python、PyTorch\n- 熟悉Stable Diffusion、ControlNet\n- 有视频生成项目经验\n- 硕士及以上",
        "expected": {"should_recommend": True, "reason": "候选人视频大模型研究处于SOTA水平"},
        "key_skills": ["Python", "PyTorch", "AIGC", "Diffusion Model"],
        "required_years": 2,
        "education": "硕士"
    },
    {
        "jd_id": "J018",
        "jd_text": "前端开发工程师（React方向）\n地点：上海\n经验：2年以上\n要求：\n- 精通React、TypeScript\n- 熟悉Next.js\n- 有复杂SPA开发经验\n- 本科及以上学历",
        "expected": {"should_recommend": False, "reason": "候选人是后端方向"},
        "key_skills": ["React", "TypeScript", "Next.js"],
        "required_years": 2,
        "education": "本科"
    },
    {
        "jd_id": "J019",
        "jd_text": "临床研发经理（制药方向）\n地点：苏州\n经验：5年以上\n要求：\n- 临床医学/药学博士\n- 有新药临床试验经验\n- 熟悉FDA/ NMPA申报流程\n- 团队管理能力",
        "expected": {"should_recommend": True, "reason": "候选人临床背景深厚且有AI医疗落地经验"},
        "key_skills": ["Clinical Research", "PhD Medicine", "FDA"],
        "required_years": 5,
        "education": "博士"
    },
    {
        "jd_id": "J020",
        "jd_text": "农业技术推广专员\n地点：黑龙江\n经验：1年以上\n要求：\n- 农学相关专业本科\n- 有基层农技推广经验\n- 适应农村工作环境\n- 吃苦耐劳",
        "expected": {"should_recommend": False, "reason": "岗位与候选人背景完全不匹配"},
        "key_skills": ["Agriculture", "Extension Services"],
        "required_years": 1,
        "education": "本科"
    },
]

if __name__ == "__main__":
    import json
    with open("eval_dataset.json", "w", encoding="utf-8") as f:
        json.dump({"resumes": RESUMES, "jobs": JOBS}, f, ensure_ascii=False, indent=2)
    print(f"✅ 已生成 {len(RESUMES)} 份简历，{len(JOBS)} 个JD")
    print("   数据已保存到 eval_dataset.json")
