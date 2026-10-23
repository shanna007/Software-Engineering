import ast
import re
import json
from agent_base import Agent
from test_runner import run_unittest


class TestAgent(Agent):
    """根据需求和实现生成测试，并运行测试获得反馈。"""

    def __init__(self, llm):
        super().__init__("TestAgent", llm)

    def run(self, state):
        if not state.generated_code:
            raise ValueError("缺少生成代码，无法进行测试。")

        self.log(state, "根据需求、设计和代码生成 unittest 测试。")
        prompt = """
你是一名严谨的 Python 测试工程师。
为提供的 generated_code.py 编写独立的 unittest 测试文件。
只输出 Python 测试代码，不要 Markdown 代码围栏。
必须 import unittest，并使用 class Test... (unittest.TestCase)。
测试应覆盖核心功能、正常输入、边界情况和无效输入。
被测模块名固定为 generated_code。
尽量只测试公开函数/类接口，不要依赖内部实现细节。
测试应可重复，不访问网络、环境变量、真实用户文件或系统资源。
不要使用 mock 来掩盖被测功能缺陷，不要自行修改应用代码。
"""
        user_prompt = (
            "【需求规格】\n"
            + json.dumps(state.requirement_spec, ensure_ascii=False, indent=2)
            + "\n【设计文档】\n"
            + json.dumps(state.design_doc, ensure_ascii=False, indent=2)
            + "\n【待测源码 generated_code.py】\n"
            + state.generated_code
        )
        tests = self.llm.generate_text(
            prompt, user_prompt, self.name, state
        )
        tests = re.sub(
            r"^```(?:python)?\s*", "", tests.strip(),
            count=1, flags=re.IGNORECASE
        )
        tests = re.sub(r"\s*```$", "", tests, count=1).strip()
        if not tests:
            raise ValueError("TestAgent 未生成测试代码。")

        try:
            ast.parse(tests)
        except SyntaxError as exc:
            raise ValueError(f"生成测试代码语法错误：{exc}") from exc

        state.generated_tests = tests
        state.agent_outputs[self.name] = tests
        self.send_message(
            state, "TestRunner", "test_code",
            {"test_code_length": len(tests)}
        )

        self.log(state, "开始进行静态安全筛查并运行测试。")
        report = run_unittest(
            source_code=state.generated_code,
            test_code=state.generated_tests,
            timeout=10,
        )
        state.test_report = report
        self.send_message(
            state, "Workflow", "test_report", report
        )

        self.log(
            state,
            f"测试执行状态：{report['status']}"
        )
        if report["status"] != "passed":
            raise RuntimeError(
                "自动测试未通过，详见 state.test_report。"
            )

        return report
