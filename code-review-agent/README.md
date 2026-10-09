# 代码审查助手 Agent
基于LangChain构建的智能代码审查Agent，自动分析代码质量、发现潜在Bug、给出专业改进建议。

## 功能特性
- ✅ 多维度代码审查：Bug检测、规范检查、性能分析、安全审计
- ✅ 工具集成：支持读取本地代码文件进行审查
- ✅ 上下文记忆：支持多轮对话追问
- ✅ 错误重试：API调用失败自动重试，提升稳定性
- ✅ 命令行交互：开箱即用，简单易用

## 技术栈
- 编程语言：Python 3.10+
- Agent框架：LangChain
- 核心模式：ReAct 推理-行动循环
- LLM：支持所有OpenAI兼容模型

## 目录结构
```
code-review-agent/
├── src/
│   ├── __init__.py    # 空文件，标识Python包
│   ├── config.py      # 配置管理
│   ├── prompts.py     # Prompt模板
│   ├── tools.py       # 自定义工具
│   └── agent.py       # Agent核心逻辑
├── main.py            # 程序入口
├── requirements.txt   # 依赖清单
├── .env               # 环境变量示例
├── README.md          # 使用文档
└── Design.md          # 设计文档
```

## 代码仓库地址
```
https://github.com/shanna007/Software-Engineering/tree/main/code-review-agent
```

## 快速开始
### 1. 安装依赖
```bash
pip install -r requirements.txt
```
### 2.配置环境变量
复制.env.example为.env，填入你的ARK_API_KEY、BASE_URL、LLM_MODEL等信息，示例如下：
```bash
ARK_API_KEY=xxx
BASE_URL=https://ark.cn-beijing.volces.com/api/v3
LLM_MODEL=ep-xxxx
```
### 3.运行
```
python main.py
```
