from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from openai import APIError, RateLimitError, APIConnectionError
from src.config import ARK_API_KEY, BASE_URL, LLM_MODEL, TEMPERATURE, MAX_RETRY, MAX_ITERATIONS
from src.prompts import REACT_AGENT_SYSTEM_PROMPT
from src.tools import tool_list
from langgraph.errors import GraphRecursionError
from langchain_core.messages import HumanMessage, AIMessage

class CodeReviewAgent:
    def __init__(self, max_rounds: int = None):
        if not ARK_API_KEY:
            raise RuntimeError("未配置 ARK_API_KEY，请检查根目录 .env 文件")
        if max_rounds is None:
            max_rounds = MAX_ITERATIONS
        self.max_rounds = max_rounds
        self.llm = ChatOpenAI(
            api_key=ARK_API_KEY,
            base_url=BASE_URL,
            model=LLM_MODEL,
            temperature=TEMPERATURE
        )
        self.agent = create_react_agent(
            model=self.llm,
            tools=tool_list,
            prompt=REACT_AGENT_SYSTEM_PROMPT
        )
        # 维护会话消息历史，实现多轮记忆
        self.chat_history = []

    @retry(
        stop=stop_after_attempt(MAX_RETRY),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((APIError, RateLimitError, APIConnectionError)),
        reraise=True
    )
    def run(self, user_input: str) -> str:
        # 追加用户消息（必须是HumanMessage对象，不能用元组）
        self.chat_history.append(HumanMessage(content=user_input))

        try:
            result = self.agent.invoke(
                {"messages": self.chat_history},
                config={
                    "recursion_limit": self.max_rounds
                }
            )
        except GraphRecursionError:
            return f"Agent 达到最大轮次限制 {self.max_rounds}，疑似工具调用死循环，已强制终止。请精简你的查询。"

        # 更新完整会话历史（全部是Message对象）
        self.chat_history = result["messages"]

        if not self.chat_history:
            return "Agent返回消息为空"

        # 修复边界case：找到最后一条AI输出消息，跳过工具/系统消息
        final_message = None
        for msg in reversed(self.chat_history):
            if isinstance(msg, AIMessage):
                final_message = msg
                break

        if final_message is None:
            return "Agent未能生成有效回复，未获取到AI输出。"
        # final_message = self.chat_history[-1]
        return final_message.content

