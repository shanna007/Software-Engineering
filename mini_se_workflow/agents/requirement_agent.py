import json
from agent_base import Agent


REQUIREMENT_SCHEMA = {
    "type": "object",
    "properties": {
        "project_name": {"type": "string"},
        "goal": {"type": "string"},
        "user_roles": {"type": "array", "items": {"type": "string"}},
        "functional_requirements": {
            "type": "array", "items": {"type": "string"}
        },
        "non_functional_requirements": {
            "type": "array", "items": {"type": "string"}
        },
        "constraints": {"type": "array", "items": {"type": "string"}},
        "acceptance_criteria": {
            "type": "array", "items": {"type": "string"}
        },
        "assumptions": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "project_name", "goal", "user_roles", "functional_requirements",
        "non_functional_requirements", "constraints",
        "acceptance_criteria", "assumptions"
    ],
    "additionalProperties": False,
}


class RequirementAgent(Agent):
    def __init__(self, llm):
        super().__init__("RequirementAgent", llm)

    def run(self, state):
        raw = state.raw_requirement.strip()
        if not raw:
            raise ValueError("原始需求不能为空。")

        self.log(state, "开始进行需求分析。")
        prompt = """
你是一名资深软件需求分析师。请把用户原始描述整理成可执行、可验证的需求规格。
区分用户明确提出的要求与合理假设；不要虚构用户没有提出的硬性约束。
功能需求与验收标准应尽量具体。输出必须符合指定 JSON Schema。
"""
        spec = self.llm.generate_json(
            system_prompt=prompt,
            user_prompt=f"请分析以下软件需求：\n{raw}",
            agent_name=self.name,
            state=state,
            schema_name="requirement_spec",
            schema=REQUIREMENT_SCHEMA,
        )
        if not spec["functional_requirements"]:
            raise ValueError("需求规格至少需要一项功能需求。")

        state.requirement_spec = spec
        state.agent_outputs[self.name] = json.dumps(
            spec, ensure_ascii=False, indent=2
        )
        self.send_message(
            state, "DesignAgent", "requirement_spec", spec
        )
        self.log(state, "需求规格已生成并写入共享状态。")
        return spec
