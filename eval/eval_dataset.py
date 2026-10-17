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
        "key_skills": ["PyTorch", "Computer Vision", "TensorRT", "CUDA", "计算机视觉", "目标检测"],
        "required_years": 2,
        "education": "硕士"
    },
    {
        "jd_id": "J004",
        "jd_text": "数据分析师（电商方向）\n地点：杭州\n经验：1-3年\n要求：\n- 精通SQL和Python\n- 熟练使用Tableau/Power BI\n- 有AB测试经验\n- 对数据敏感，逻辑清晰",
        "expected": {"should_recommend": True, "reason": "候选人数据分析和AB测试经验丰富"},
        "key_skills": ["SQL", "Python", "Tableau", "AB Testing", "数据分析", "统计分析", "AB测试"],
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
        "key_skills": ["AI产品", "提示词工程", "数据分析", "产品管理", "AIGC", "大模型", "需求分析"],
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
        "key_skills": ["SolidWorks", "ANSYS", "机械设计", "结构设计"],
        "required_years": 3,
        "education": "本科"
    },
    {
        "jd_id": "J011",
        "jd_text": "量化交易研究员\n地点：上海\n经验：3年以上\n要求：\n- 数学/物理/金融工程背景\n- 精通Python、C++\n- 有量化策略开发经验\n- 熟悉时序预测、强化学习\n- 硕士及以上",
        "expected": {"should_recommend": True, "reason": "候选人量化投研背景与岗位要求契合"},
        "key_skills": ["Python", "C++", "量化交易", "量化", "金融建模", "时序预测"],
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
        "key_skills": ["Python", "LLM安全", "渗透测试", "Go", "AI安全", "漏洞挖掘"],
        "required_years": 2,
        "education": "博士"
    },
    {
        "jd_id": "J014",
        "jd_text": "外贸业务员\n地点：宁波\n经验：1年以上\n要求：\n- 英语CET-6\n- 有B2B外贸经验\n- 熟悉阿里巴巴国际站\n- 本科及以上学历",
        "expected": {"should_recommend": False, "reason": "候选人方向不符"},
        "key_skills": ["英语", "跨境电商", "B2B外贸", "海外市场", "客户开发"],
        "required_years": 1,
        "education": "本科"
    },
    {
        "jd_id": "J015",
        "jd_text": "自动驾驶感知算法工程师\n地点：北京\n经验：3年以上\n要求：\n- 精通C++/Python\n- 熟悉视觉/激光雷达融合感知\n- 有量产项目经验\n- 硕士及以上",
        "expected": {"should_recommend": True, "reason": "候选人自动驾驶领域资深专家"},
        "key_skills": ["C++", "Python", "感知", "传感器融合", "目标检测"],
        "required_years": 3,
        "education": "硕士"
    },
    {
        "jd_id": "J016",
        "jd_text": "人力资源BP\n地点：北京\n经验：3年以上\n要求：\n- 有互联网公司HRBP经验\n- 熟悉招聘、员工关系、绩效管理\n- 良好的沟通能力\n- 本科及以上学历",
        "expected": {"should_recommend": False, "reason": "岗位方向完全不同"},
        "key_skills": ["招聘", "员工关系", "绩效管理", "HR", "人才盘点"],
        "required_years": 3,
        "education": "本科"
    },
    {
        "jd_id": "J017",
        "jd_text": "视频算法工程师（AIGC方向）\n地点：杭州\n经验：2年以上\n要求：\n- 精通Python、PyTorch\n- 熟悉Stable Diffusion、ControlNet\n- 有视频生成项目经验\n- 硕士及以上",
        "expected": {"should_recommend": True, "reason": "候选人视频大模型研究处于SOTA水平"},
        "key_skills": ["Python", "PyTorch", "AIGC", "视频生成", "视频理解"],
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
        "key_skills": ["临床研究", "临床医学", "医学", "药品", "FDA", "临床试验", "药品注册"],
        "required_years": 5,
        "education": "博士"
    },
    {
        "jd_id": "J020",
        "jd_text": "农业技术推广专员\n地点：黑龙江\n经验：1年以上\n要求：\n- 农学相关专业本科\n- 有基层农技推广经验\n- 适应农村工作环境\n- 吃苦耐劳",
        "expected": {"should_recommend": False, "reason": "岗位与候选人背景完全不匹配"},
        "key_skills": ["农业", "农技推广", "种植", "农业服务"],
        "required_years": 1,
        "education": "本科"
    },
    {
        "jd_id": "J021",
        "jd_text": "UX设计师\n地点：北京\n经验：1年以上\n要求：\n- 精通Figma、Principle\n- 熟悉UX/UI设计流程\n- 有AI工具设计经验\n- 有作品集",
        "expected": {"should_recommend": True, "reason": "候选人UX设计方向匹配"},
        "key_skills": ["Figma", "Principle", "UX", "交互设计", "用户研究", "原型设计"],
        "required_years": 1,
        "education": "本科"
    },
    {
        "jd_id": "J022",
        "jd_text": "法务合规专员\n地点：北京\n经验：3年以上\n要求：\n- 熟悉知识产权与合同审查\n- 了解AI相关法规（生成式AI管理办法）\n- 有互联网公司法务经验",
        "expected": {"should_recommend": True, "reason": "候选人法律合规背景匹配"},
        "key_skills": ["法律合规", "知识产权", "合同审查", "生成式AI", "数据合规"],
        "required_years": 3,
        "education": "本科"
    },
    {
        "jd_id": "J023",
        "jd_text": "网络运维工程师\n地点：广州\n经验：2年以上\n要求：\n- 熟悉Linux/网络协议\n- 有5G/基站运维经验\n- 会Python自动化脚本\n- 责任心强",
        "expected": {"should_recommend": True, "reason": "候选人网络运维经验匹配"},
        "key_skills": ["网络运维", "5G", "Linux", "自动化", "监控", "Python"],
        "required_years": 2,
        "education": "本科"
    },
    {
        "jd_id": "J024",
        "jd_text": "财务分析师\n地点：上海\n经验：3年以上\n要求：\n- 熟悉财务建模与报表分析\n- 熟练使用Excel、SQL、Python(pandas)\n- 有上市公司审计经验者优先",
        "expected": {"should_recommend": True, "reason": "候选人财务分析方向匹配"},
        "key_skills": ["财务建模", "Excel", "SQL", "pandas", "审计", "报表分析"],
        "required_years": 3,
        "education": "本科"
    },
    {
        "jd_id": "J025",
        "jd_text": "芯片设计工程师\n地点：上海\n经验：3年以上\n要求：\n- 精通Verilog/SystemVerilog\n- 有SoC芯片架构设计经验\n- 熟悉模拟电路/数字前端\n- 有流片经验优先",
        "expected": {"should_recommend": True, "reason": "候选人IC设计与芯片架构背景匹配"},
        "key_skills": ["Verilog", "SystemVerilog", "芯片架构", "模拟电路", "SoC", "流片"],
        "required_years": 3,
        "education": "硕士"
    },
    {
        "jd_id": "J026",
        "jd_text": "量子计算研究员\n地点：北京\n经验：3年以上\n要求：\n- 物理/计算机博士优先\n- 精通量子算法与量子纠错\n- 有量子编译器开发经验\n- 发表顶刊论文优先",
        "expected": {"should_recommend": True, "reason": "候选人量子计算方向深度匹配"},
        "key_skills": ["量子计算", "量子纠错", "量子算法", "量子编译器", "Python"],
        "required_years": 3,
        "education": "博士"
    },
    {
        "jd_id": "J027",
        "jd_text": "视频特效师\n地点：杭州\n经验：2年以上\n要求：\n- 精通AE、PR\n- 熟悉Blender等三维工具\n- 有视频特效/合成项目经验\n- 有作品集",
        "expected": {"should_recommend": True, "reason": "候选人视频特效方向匹配"},
        "key_skills": ["AE", "PR", "Blender", "特效合成", "后期制作"],
        "required_years": 2,
        "education": "本科"
    },
    {
        "jd_id": "J028",
        "jd_text": "建筑结构工程师\n地点：武汉\n经验：3年以上\n要求：\n- 精通AutoCAD、PKPM、Revit\n- 有高层建筑设计经验\n- 熟悉国家结构设计规范\n- 有项目管理经验优先",
        "expected": {"should_recommend": True, "reason": "候选人建筑结构背景匹配"},
        "key_skills": ["AutoCAD", "PKPM", "Revit", "结构设计", "高层建筑", "施工管理"],
        "required_years": 3,
        "education": "本科"
    },
    {
        "jd_id": "J029",
        "jd_text": "供应链管理专员\n地点：深圳\n经验：2年以上\n要求：\n- 熟悉采购与供应商管理\n- 有跨境选品与供应链优化经验\n- 熟悉国际物流\n- 英语流利优先",
        "expected": {"should_recommend": True, "reason": "候选人供应链方向匹配"},
        "key_skills": ["供应链", "采购", "选品", "物流", "跨境电商", "英语"],
        "required_years": 2,
        "education": "本科"
    },
    {
        "jd_id": "J030",
        "jd_text": "推荐算法工程师\n地点：北京\n经验：3年以上\n要求：\n- 精通推荐系统召回/排序\n- 熟练使用TensorFlow、PyTorch\n- 有时空序列预测经验\n- 有大流量业务优化经验优先",
        "expected": {"should_recommend": True, "reason": "候选人推荐系统与排序经验深度匹配"},
        "key_skills": ["推荐系统", "排序", "特征工程", "深度学习", "时空预测", "TensorFlow"],
        "required_years": 3,
        "education": "硕士"
    },
    {
        "jd_id": "J031",
        "jd_text": "品牌设计师\n地点：上海\n经验：2年以上\n要求：\n- 精通PS、AI\n- 有品牌视觉/电商大促设计经验\n- 审美在线，创意能力强\n- 有完整作品集",
        "expected": {"should_recommend": True, "reason": "候选人品牌设计背景匹配"},
        "key_skills": ["品牌设计", "PS", "AI", "创意设计", "视觉传达", "电商设计"],
        "required_years": 2,
        "education": "本科"
    },
    {
        "jd_id": "J032",
        "jd_text": "行业研究员\n地点：深圳\n经验：3年以上\n要求：\n- 熟悉行业研究与深度报告撰写\n- 有TMT/科技赛道研究经验\n- 熟练使用Excel/数据工具\n- 逻辑清晰、表达能力强",
        "expected": {"should_recommend": True, "reason": "候选人行业研究背景匹配"},
        "key_skills": ["行业研究", "深度报告", "TMT", "数据分析", "Excel"],
        "required_years": 3,
        "education": "硕士"
    },
    {
        "jd_id": "J033",
        "jd_text": "通信协议工程师\n地点：北京\n经验：3年以上\n要求：\n- 精通C语言\n- 有5G/4G协议栈开发经验\n- 参与过通信标准制定优先\n- 熟悉LTE/NR协议架构",
        "expected": {"should_recommend": True, "reason": "候选人5G协议开发背景匹配"},
        "key_skills": ["5G", "协议栈", "C语言", "通信标准", "LTE", "NR"],
        "required_years": 3,
        "education": "硕士"
    },
    {
        "jd_id": "J034",
        "jd_text": "食品研发工程师\n地点：呼和浩特\n经验：3年以上\n要求：\n- 食品科学/生物工程背景\n- 有配方研发与工艺优化经验\n- 熟悉食品安全法规\n- 有团队管理经验优先",
        "expected": {"should_recommend": True, "reason": "候选人食品研发背景匹配"},
        "key_skills": ["食品研发", "配方", "工艺优化", "食品科学", "质量管理"],
        "required_years": 3,
        "education": "硕士"
    },
    {
        "jd_id": "J035",
        "jd_text": "用户研究员\n地点：杭州\n经验：2年以上\n要求：\n- 熟悉问卷、访谈、可用性测试\n- 会用眼动实验等研究方法\n- 能输出用户洞察报告\n- 有游戏/互联网研究经验优先",
        "expected": {"should_recommend": True, "reason": "候选人用户研究背景匹配"},
        "key_skills": ["用户研究", "问卷", "访谈", "可用性测试", "眼动实验", "数据分析"],
        "required_years": 2,
        "education": "硕士"
    },
    {
        "jd_id": "J036",
        "jd_text": "技术翻译\n地点：北京\n经验：2年以上\n要求：\n- 精通英语/德语\n- 有技术文档翻译经验\n- 有跨国项目协调经验优先\n- 汽车/制造行业背景加分",
        "expected": {"should_recommend": True, "reason": "候选人翻译与项目管理背景匹配"},
        "key_skills": ["翻译", "技术文档", "英语", "德语", "项目管理"],
        "required_years": 2,
        "education": "本科"
    },
    {
        "jd_id": "J037",
        "jd_text": "CAE仿真工程师\n地点：北京\n经验：3年以上\n要求：\n- 精通ANSYS等仿真软件\n- 有热分析/结构仿真经验\n- 熟悉流体或热防护方向\n- 有航天/军工经验优先",
        "expected": {"should_recommend": True, "reason": "候选人仿真与热防护背景匹配"},
        "key_skills": ["ANSYS", "仿真", "热分析", "结构力学", "流体", "热防护"],
        "required_years": 3,
        "education": "硕士"
    },
    {
        "jd_id": "J038",
        "jd_text": "教研老师（数学）\n地点：北京\n经验：2年以上\n要求：\n- 数学功底扎实\n- 有课程研发/教研经验\n- 熟悉K12教学大纲\n- 有线上教育经验优先",
        "expected": {"should_recommend": True, "reason": "候选人数学教研背景匹配"},
        "key_skills": ["数学", "教研", "课程设计", "教学设计", "K12"],
        "required_years": 2,
        "education": "本科"
    },
    {
        "jd_id": "J039",
        "jd_text": "内容策划\n地点：上海\n经验：3年以上\n要求：\n- 文案功底强\n- 有品牌内容策划经验\n- 熟悉社交媒体营销\n- 有团队管理经验优先",
        "expected": {"should_recommend": True, "reason": "候选人内容策划背景匹配"},
        "key_skills": ["内容策划", "文案", "创意", "品牌营销", "社交媒体"],
        "required_years": 3,
        "education": "本科"
    },
    {
        "jd_id": "J040",
        "jd_text": "航运调度主管\n地点：上海\n经验：5年以上\n要求：\n- 有远洋航行经验（船长/大副优先）\n- 熟悉船队调度与航运管理\n- 英语可作工作语言\n- 持相关航海证书",
        "expected": {"should_recommend": True, "reason": "候选人远洋船长与调度背景匹配"},
        "key_skills": ["航海技术", "船队调度", "航运管理", "英语", "远洋航行"],
        "required_years": 5,
        "education": "大专"
    },
    {
        "jd_id": "J041",
        "jd_text": "轮机工程师\n地点：上海\n经验：3年以上\n要求：\n- 持轮机长/轮机员证书\n- 熟悉船舶动力与机电设备\n- 有远洋船舶技术管理经验\n- 英语可作为工作语言",
        "expected": {"should_recommend": True, "reason": "候选人轮机工程背景匹配"},
        "key_skills": ["轮机工程", "船舶动力", "船舶技术", "机械", "英语"],
        "required_years": 3,
        "education": "大专"
    },
    {
        "jd_id": "J042",
        "jd_text": "插画师\n地点：不限\n经验：1年以上\n要求：\n- 手绘功底强\n- 熟悉PS/Procreate\n- 有商业接单与版权授权经验\n- 有个人作品集",
        "expected": {"should_recommend": True, "reason": "候选人独立插画背景匹配"},
        "key_skills": ["插画", "绘画", "PS", "Procreate", "版权授权"],
        "required_years": 1,
        "education": "不限"
    },
    {
        "jd_id": "J043",
        "jd_text": "投资分析师\n地点：北京\n经验：3年以上\n要求：\n- 有行业研究与投资分析经验\n- 熟悉尽调流程与估值建模\n- 关注新能源/科技赛道\n- 有PE/VC经验优先",
        "expected": {"should_recommend": True, "reason": "候选人投资研究背景匹配"},
        "key_skills": ["投资分析", "尽调", "估值建模", "行业研究", "新能源"],
        "required_years": 3,
        "education": "硕士"
    },
    {
        "jd_id": "J044",
        "jd_text": "纺织面料工程师\n地点：泉州\n经验：3年以上\n要求：\n- 纺织工程/材料背景\n- 有功能性面料开发经验\n- 熟悉面料工艺与测试\n- 有运动品牌经验优先",
        "expected": {"should_recommend": True, "reason": "候选人面料开发背景匹配"},
        "key_skills": ["面料开发", "纺织工程", "材料", "工艺", "测试"],
        "required_years": 3,
        "education": "硕士"
    },
    {
        "jd_id": "J045",
        "jd_text": "显示技术工程师\n地点：深圳\n经验：5年以上\n要求：\n- 熟悉OLED/显示面板技术\n- 有光电材料开发经验\n- 熟悉显示驱动与良率优化\n- 有团队管理经验优先",
        "expected": {"should_recommend": True, "reason": "候选人OLED显示背景匹配"},
        "key_skills": ["OLED", "显示技术", "光电", "材料开发", "面板"],
        "required_years": 5,
        "education": "硕士"
    },
    {
        "jd_id": "J046",
        "jd_text": "演员\n地点：横店/北京\n经验：1年以上\n要求：\n- 表演功底扎实\n- 有影视/网剧出演经验\n- 台词与形体训练扎实\n- 配合度高",
        "expected": {"should_recommend": True, "reason": "候选人演艺背景匹配"},
        "key_skills": ["表演", "台词", "影视", "网剧", "角色塑造"],
        "required_years": 1,
        "education": "不限"
    },
    {
        "jd_id": "J047",
        "jd_text": "课程研发总监（英语）\n地点：北京\n经验：5年以上\n要求：\n- 英语专业/教学背景\n- 有英语课程体系重构经验\n- 熟悉教学管理与师资培养\n- 有在线教育经验优先",
        "expected": {"should_recommend": True, "reason": "候选人英语教学与课程研发背景匹配"},
        "key_skills": ["课程研发", "英语", "教学管理", "课程体系", "师资培养"],
        "required_years": 5,
        "education": "硕士"
    },
    {
        "jd_id": "J048",
        "jd_text": "给排水工程师\n地点：广州\n经验：3年以上\n要求：\n- 精通AutoCAD、WaterCAD\n- 有市政管网设计经验\n- 熟悉污水处理工艺\n- 有水务项目管理经验优先",
        "expected": {"should_recommend": True, "reason": "候选人给排水设计背景匹配"},
        "key_skills": ["给排水", "AutoCAD", "WaterCAD", "管网设计", "污水处理", "水务"],
        "required_years": 3,
        "education": "本科"
    },
    {
        "jd_id": "J049",
        "jd_text": "兽医\n地点：深圳\n经验：2年以上\n要求：\n- 动物医学专业\n- 擅长犬猫外科手术\n- 有宠物医院临床经验\n- 执业兽医师资格证",
        "expected": {"should_recommend": True, "reason": "候选人兽医临床背景匹配"},
        "key_skills": ["兽医", "外科手术", "动物医学", "宠物医疗", "临床"],
        "required_years": 2,
        "education": "本科"
    },
    {
        "jd_id": "J050",
        "jd_text": "文物修复师\n地点：北京\n经验：3年以上\n要求：\n- 熟悉青铜器/陶瓷修复\n- 有博物馆修复工作经验\n- 掌握材料分析与传统工艺\n- 有文物保护意识",
        "expected": {"should_recommend": True, "reason": "候选人文物修复背景匹配"},
        "key_skills": ["文物修复", "青铜器", "陶瓷修复", "文物保护", "材料分析"],
        "required_years": 3,
        "education": "硕士"
    },
    {
        "jd_id": "J051",
        "jd_text": "资产评估师\n地点：上海\n经验：3年以上\n要求：\n- 持有资产评估师证书\n- 有企业并购估值经验\n- 熟悉财务分析与尽调\n- 有上市公司评估经验优先",
        "expected": {"should_recommend": True, "reason": "候选人资产评估背景匹配"},
        "key_skills": ["资产评估", "估值", "并购", "财务分析", "尽调"],
        "required_years": 3,
        "education": "本科"
    },
    {
        "jd_id": "J052",
        "jd_text": "隧道工程师\n地点：成都\n经验：3年以上\n要求：\n- 土木工程/岩土背景\n- 有深埋隧道施工经验\n- 熟悉盾构施工技术\n- 有现场技术管理经验",
        "expected": {"should_recommend": True, "reason": "候选人隧道工程背景匹配"},
        "key_skills": ["隧道工程", "盾构", "土木工程", "岩土", "施工管理", "CAD"],
        "required_years": 3,
        "education": "本科"
    },
    {
        "jd_id": "J053",
        "jd_text": "材料科研工程师\n地点：苏州\n经验：1年以上\n要求：\n- 材料/化学背景\n- 有纳米材料/二维材料合成经验\n- 熟悉实验室分析仪器\n- 有科研论文发表优先",
        "expected": {"should_recommend": True, "reason": "候选人材料科研背景匹配"},
        "key_skills": ["纳米材料", "二维材料", "材料合成", "实验室", "化学"],
        "required_years": 1,
        "education": "硕士"
    },
    {
        "jd_id": "J054",
        "jd_text": "机器人算法工程师\n地点：深圳\n经验：2年以上\n要求：\n- 精通Python、C++\n- 熟悉ROS、Gazebo等机器人开发框架\n- 有路径规划/运动控制算法经验\n- 有无人机/机器人产品落地经验优先",
        "expected": {"should_recommend": True, "reason": "候选人机器人路径规划背景匹配"},
        "key_skills": ["Python", "C++", "ROS", "Gazebo", "路径规划", "运动控制"],
        "required_years": 2,
        "education": "硕士"
    },
]

if __name__ == "__main__":
    import json
    with open("eval_dataset.json", "w", encoding="utf-8") as f:
        json.dump({"resumes": RESUMES, "jobs": JOBS}, f, ensure_ascii=False, indent=2)
    print(f"✅ 已生成 {len(RESUMES)} 份简历，{len(JOBS)} 个JD")
    print("   数据已保存到 eval_dataset.json")
