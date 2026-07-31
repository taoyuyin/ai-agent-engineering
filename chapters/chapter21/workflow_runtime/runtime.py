from dataclasses import dataclass
from typing import Callable, Dict, List, Set, Tuple


@dataclass
class Task:
    task_id: str
    function: Callable[[Dict[str, object]], Dict[str, object]]
    depends_on: Tuple[str, ...] = ()
    approval: bool = False
    status: str = "pending"
    attempts: int = 0
    max_retries: int = 1


class Workflow:
    def __init__(self, tasks: List[Task]) -> None:
        self.tasks = {task.task_id: task for task in tasks}
        self.state = {}  # type: Dict[str, object]
        self.approvals = set()  # type: Set[str]

    def approve(self, task_id: str) -> None:
        self.approvals.add(task_id)

    def run_until_blocked(self) -> None:
        while True:
            completed = {key for key, task in self.tasks.items() if task.status == "completed"}
            ready = [
                task
                for task in self.tasks.values()
                if task.status in {"pending", "retry"}
                and set(task.depends_on) <= completed
                and (not task.approval or task.task_id in self.approvals)
            ]
            if not ready:
                return
            for task in ready:
                try:
                    task.attempts += 1
                    self.state.update(task.function(dict(self.state)))
                    task.status = "completed"
                except (RuntimeError, TimeoutError):
                    task.status = "retry" if task.attempts <= task.max_retries else "failed"

    def statuses(self) -> Dict[str, str]:
        return {key: task.status for key, task in self.tasks.items()}
