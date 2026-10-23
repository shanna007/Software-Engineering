# Mini SE Multi-Agent Workflow Plus

## 项目简介

这是一个原生 Python 的顺序式多 Agent 软件开发工作流，包含：

1. RequirementAgent：需求分析，使用 JSON Schema 结构化输出。
2. DesignAgent：系统设计，使用 JSON Schema 结构化输出。
3. CodeAgent：生成 Python 源码并做语法检查。
4. TestAgent：生成 unittest 测试并调用测试运行器执行。
5. Workflow：顺序调度、共享状态、日志、错误处理。
6. LLMClient：统一封装模型调用。

## 环境

- Python 3.10+
- OpenAI Python SDK
- python-dotenv
- 一个支持 Responses API 和 JSON Schema Structured Outputs 的模型

## 配置

复制 `.env.example` 为 `.env`，填入有效配置：

    OPENAI_API_KEY=你的密钥
    OPENAI_MODEL=服务支持的模型名称

不要提交真实密钥。

## 安装与运行

    python -m pip install -r requirements.txt
    python main.py

输入自然语言软件需求。每个 Agent 的实际输出、消息记录、日志和测试报告会保存在 `outputs/`。

## 输出

- requirement.json：标准化需求
- design.json：系统设计
- generated_code.py：生成的应用代码
- test_generated.py：生成的测试代码
- test_report.json：测试执行结果
- execution_report.json：Workflow 状态、日志、消息和各 Agent 输出

## 结构化输出

RequirementAgent 和 DesignAgent 使用 Responses API 的 JSON Schema 格式约束输出。
Schema 使用 `strict: true`、`additionalProperties: false`，并声明必填字段。
所选模型必须支持对应的 Structured Outputs 功能。

## 自动测试流程

TestAgent 根据需求、设计和实现生成 unittest。
测试运行器会先进行 AST 静态检查，再在临时目录中的子进程执行测试，并设置超时。
测试失败或测试运行器拒绝代码时，Workflow 会标记为 failed。

## 安全限制（重要）

Python 子进程和 AST 检查不是强安全沙箱。恶意代码可能绕过简单静态检查。
因此：
- 不要对不可信来源的模型代码直接执行。
- 运行前应审查生成代码。
- 更强的隔离需要使用无网络、低权限、限制资源的容器或虚拟机。
- 当前 MVP 不自动修复失败代码，避免无限循环和不可控 API 费用。
- 测试通过只说明当前测试用例通过，不保证软件没有缺陷。

## 评审点

- 4 个 Agent 顺序协作
- 共享状态管理与消息传递
- JSON Schema 结构化输出
- 生成代码语法检查
- 自动生成并运行单元测试
- 异常处理与测试报告
- 模块化设计，方便新增 Agent

## 工作流过程追踪（新增）

运行后，`outputs/` 除原有产物外，还会生成：

- `workflow_trace.jsonl`：逐事件记录 Agent 开始/结束、输入状态快照、输出摘要、耗时、异常、Agent 消息，以及 LLM 调用的提示词、JSON Schema 和模型回复。
- `workflow_report.md`：便于阅读和答辩展示的 Markdown 报告，包含 Agent 执行顺序、共享状态快照、Agent 间消息和测试结果。
- `execution_report.json`：同时包含 logs、messages、events 和 agent_outputs。

注意：追踪日志可能包含完整需求、提示词、生成代码和模型回复。分享日志前请检查是否包含 API 密钥、个人信息或其他敏感内容。日志记录的是模型可见输入/输出与执行事件，不是模型的隐藏思维链。
