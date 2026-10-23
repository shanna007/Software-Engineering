import ast
import re
import json
from agent_base import Agent


class CodeAgent(Agent):
    def __init__(self, llm):
        super().__init__("CodeAgent", llm)

    def run(self, state):
        if not state.requirement_spec or not state.design_doc:
            raise ValueError("缺少需求规格或设计文档。")

        self.log(state, "根据需求和设计生成完整 Python 程序。")
        prompt = """
你是一名资深 Python 工程师。根据需求规格和设计文档生成完整的 Python 程序。
只输出 Python 源码，不要使用 Markdown 代码围栏。
实现核心功能、输入校验和必要异常处理；优先使用标准库。
应提供可测试的函数或类，并包含 main() 入口保护：
if __name__ == "__main__": main()
导入模块时不得启动交互或产生副作用。
不要声称代码已经测试。不要加入网络请求、子进程、动态执行、
文件删除、凭据读取等与需求无关的行为。
"""
        user_prompt = (
            "【需求规格】\n"
            + json.dumps(state.requirement_spec, ensure_ascii=False, indent=2)
            + "\n【设计文档】\n"
            + json.dumps(state.design_doc, ensure_ascii=False, indent=2)
        )
        code = self.llm.generate_text(
            prompt, user_prompt, self.name, state
        )
        code = re.sub(
            r"^```(?:python)?\s*", "", code.strip(),
            count=1, flags=re.IGNORECASE
        )
        code = re.sub(r"\s*```$", "", code, count=1).strip()
        if not code:
            raise ValueError("模型没有生成代码。")

        try:
            ast.parse(code)
        except SyntaxError as exc:
            raise ValueError(f"生成代码语法错误：{exc}") from exc

        state.generated_code = code
        state.agent_outputs[self.name] = code
        self.send_message(
            state, "TestAgent", "source_code", {
                "code_length": len(code),
                "design": state.design_doc,
            }
        )
        self.log(state, f"代码已生成并通过语法解析，共 {len(code.splitlines())} 行。")
        return code
