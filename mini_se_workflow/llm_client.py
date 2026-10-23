import os
from openai import OpenAI


class LLMClient:
    """封装普通文本生成与 JSON Schema 结构化输出。"""

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "").strip()
        base_url = os.getenv("OPENAI_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
        if not api_key:
            raise ValueError("缺少 OPENAI_API_KEY，请配置 .env 文件。")
        if not self.model:
            raise ValueError("缺少 OPENAI_MODEL，请填写服务支持的模型名称。")

        self.client = OpenAI(api_key=api_key,base_url=base_url)

    def generate_text(self, system_prompt: str, user_prompt: str,
                      agent_name: str, state) -> str:
        state.add_log(f"[LLM] {agent_name} 调用模型 {self.model}")
        response = self.client.responses.create(
            model=self.model,
            instructions=system_prompt,
            input=user_prompt,
        )
        result = (response.output_text or "").strip()
        if not result:
            raise RuntimeError(f"{agent_name} 收到空的模型响应。")
        state.add_log(f"[LLM] {agent_name} 返回 {len(result)} 个字符")
        return result

    def generate_json(self, system_prompt: str, user_prompt: str,
                      agent_name: str, state, schema_name: str,
                      schema: dict) -> dict:
        """要求模型按 JSON Schema 返回结构化数据。"""
        import json

        state.add_log(
            f"[LLM] {agent_name} 调用结构化输出，模型={self.model}"
        )
        response = self.client.responses.create(
            model=self.model,
            instructions=system_prompt,
            input=user_prompt,
            text={
                "format": {
                    "type": "json_schema",
                    "name": schema_name,
                    "strict": True,
                    "schema": schema,
                }
            },
        )
        result = (response.output_text or "").strip()
        if not result:
            raise RuntimeError(f"{agent_name} 收到空的模型响应。")
        try:
            parsed = json.loads(result)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"{agent_name} 的结构化输出无法解析为 JSON：{exc}"
            ) from exc
        state.add_log(
            f"[LLM] {agent_name} 结构化输出成功，字符数={len(result)}"
        )
        return parsed
