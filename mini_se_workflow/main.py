import json
from pathlib import Path
from dotenv import load_dotenv

from llm_client import LLMClient
from agents import RequirementAgent, DesignAgent, CodeAgent, TestAgent
from workflow import Workflow


def main():
    load_dotenv()
    llm = LLMClient()

    raw_requirement = input(
        "请输入软件需求（例如：开发一个支持添加、查询、完成任务的待办程序）：\n> "
    ).strip()
    if not raw_requirement:
        print("需求不能为空。")
        return

    agents = [
        RequirementAgent(llm),
        DesignAgent(llm),
        CodeAgent(llm),
        TestAgent(llm),
    ]
    state = Workflow(agents).run(raw_requirement)

    out = Path("outputs")
    out.mkdir(exist_ok=True)

    artifacts = {
        "requirement.json": state.requirement_spec,
        "design.json": state.design_doc,
        "test_report.json": state.test_report,
        "execution_report.json": {
            "status": state.status,
            "error": state.error,
            "messages": state.messages,
            "logs": state.logs,
            "agent_outputs": state.agent_outputs,
        },
    }
    for filename, data in artifacts.items():
        (out / filename).write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    if state.generated_code:
        (out / "generated_code.py").write_text(
            state.generated_code, encoding="utf-8"
        )
    if state.generated_tests:
        (out / "test_generated.py").write_text(
            state.generated_tests, encoding="utf-8"
        )

    state.print_summary()
    print(f"结果目录：{out.resolve()}")
    if state.status != "completed":
        print("Workflow 未完全成功，请检查 outputs/test_report.json 和 execution_report.json。")


if __name__ == "__main__":
    main()
