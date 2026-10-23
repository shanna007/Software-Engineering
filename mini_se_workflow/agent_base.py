from abc import ABC, abstractmethod


class Agent(ABC):
    """所有 Agent 的统一基类。"""

    def __init__(self, name: str, llm):
        self.name = name
        self.llm = llm

    @abstractmethod
    def run(self, state):
        """执行当前 Agent 的任务，并返回产物。"""
        raise NotImplementedError

    def log(self, state, message: str):
        state.add_log(f"[{self.name}] {message}")

    def send_message(self, state, receiver: str, message_type: str, content):
        """将真实阶段产物记录为一条 Agent 消息。"""
        state.add_message(
            sender=self.name,
            receiver=receiver,
            message_type=message_type,
            content=content,
        )
