from agent_base import Agent
from state import WorkflowState


class Workflow:
    """顺序调度 Agent，并统一管理失败状态。"""

    def __init__(self, agents: list[Agent]):
        self.agents = agents

    def run(self, raw_requirement: str) -> WorkflowState:
        state = WorkflowState(raw_requirement=raw_requirement)
        try:
            state.set_status("running")
            state.add_log("Mini SE Workflow 开始执行。")

            for index, agent in enumerate(self.agents, start=1):
                state.add_log(
                    f"========== Step {index}/{len(self.agents)}: "
                    f"{agent.name} =========="
                )
                result = agent.run(state)
                if result is None:
                    raise RuntimeError(f"{agent.name} 未返回结果。")
                state.add_log(f"{agent.name} 执行成功。")

            state.set_status("completed")
            state.add_log("所有 Agent 与自动测试均成功完成。")

        except Exception as exc:
            state.error = f"{type(exc).__name__}: {exc}"
            state.add_log(f"[ERROR] Workflow 终止：{state.error}")
            state.set_status("failed")

        return state
