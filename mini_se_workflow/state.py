from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class WorkflowState:
    """一次 Workflow 的共享状态。"""

    raw_requirement: str
    requirement_spec: dict[str, Any] = field(default_factory=dict)
    design_doc: dict[str, Any] = field(default_factory=dict)
    generated_code: str = ""
    generated_tests: str = ""
    test_report: dict[str, Any] = field(default_factory=dict)
    messages: list[dict[str, Any]] = field(default_factory=list)
    logs: list[str] = field(default_factory=list)
    agent_outputs: dict[str, str] = field(default_factory=dict)
    status: str = "initialized"
    error: str | None = None

    def add_log(self, message: str):
        stamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{stamp}] {message}"
        self.logs.append(entry)
        print(entry)

    def add_message(self, sender: str, receiver: str,
                    message_type: str, content: Any):
        self.messages.append({
            "sender": sender,
            "receiver": receiver,
            "type": message_type,
            "content": content,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        })
        self.add_log(
            f"[MESSAGE] {sender} -> {receiver} | type={message_type}"
        )

    def set_status(self, status: str):
        self.status = status
        self.add_log(f"[STATE] status = {status}")

    def print_summary(self):
        print("\n" + "=" * 60)
        print("WORKFLOW SUMMARY")
        print("=" * 60)
        print(f"Status: {self.status}")
        print(f"Messages: {len(self.messages)}")
        print(f"Logs: {len(self.logs)}")
        print(f"Requirement ready: {bool(self.requirement_spec)}")
        print(f"Design ready: {bool(self.design_doc)}")
        print(f"Code generated: {bool(self.generated_code)}")
        print(f"Tests generated: {bool(self.generated_tests)}")
        print(f"Test report: {self.test_report.get('status', 'not run')}")
        if self.error:
            print(f"Error: {self.error}")
        print("=" * 60)
