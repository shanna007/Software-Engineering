import json
from agent_base import Agent


DESIGN_SCHEMA = {
    "type": "object",
    "properties": {
        "system_name": {"type": "string"},
        "architecture": {"type": "string"},
        "modules": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "responsibility": {"type": "string"},
                },
                "required": ["name", "responsibility"],
                "additionalProperties": False,
            },
        },
        "interfaces": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "parameters": {
                        "type": "array", "items": {"type": "string"}
                    },
                    "return_value": {"type": "string"},
                },
                "required": ["name", "parameters", "return_value"],
                "additionalProperties": False,
            },
        },
        "data_structures": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["name", "description"],
                "additionalProperties": False,
            },
        },
        "implementation_steps": {
            "type": "array", "items": {"type": "string"}
        },
        "testing_plan": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "system_name", "architecture", "modules", "interfaces",
        "data_structures", "implementation_steps", "testing_plan"
    ],
    "additionalProperties": False,
}


class DesignAgent(Agent):
    def __init__(self, llm):
        super().__init__("DesignAgent", llm)

    def run(self, state):
        if not state.requirement_spec:
            raise ValueError("缺少需求规格，无法进行设计。")

        self.log(state, "根据真实需求规格设计系统。")
        prompt = """
你是一名资深 Python 软件架构师。根据需求规格输出系统设计。
模块职责明确，接口可实现，优先采用标准库和简单架构。
设计必须覆盖所有功能需求，并给出可执行的测试计划。
输出必须符合指定 JSON Schema。
"""
        design = self.llm.generate_json(
            system_prompt=prompt,
            user_prompt=(
                "需求规格如下，请设计系统：\n"
                + json.dumps(
                    state.requirement_spec, ensure_ascii=False, indent=2
                )
            ),
            agent_name=self.name,
            state=state,
            schema_name="system_design",
            schema=DESIGN_SCHEMA,
        )
        if not design["modules"]:
            raise ValueError("设计文档至少需要一个模块。")

        state.design_doc = design
        state.agent_outputs[self.name] = json.dumps(
            design, ensure_ascii=False, indent=2
        )
        self.send_message(
            state, "CodeAgent", "design_document", design
        )
        self.log(state, "设计文档已生成并写入共享状态。")
        return design
