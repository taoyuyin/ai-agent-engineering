"""Run lifecycle state machine. Invalid transitions fail before side effects."""

from framework.contracts import RunStatus


class RunStateMachine:
    _allowed = {
        RunStatus.ACCEPTED: {RunStatus.RUNNING, RunStatus.FAILED},
        RunStatus.RUNNING: {RunStatus.COMPLETED, RunStatus.FAILED},
        RunStatus.COMPLETED: set(),
        RunStatus.FAILED: set(),
    }

    def __init__(self) -> None:
        self.status = RunStatus.ACCEPTED

    def transition(self, target: RunStatus) -> RunStatus:
        if target not in self._allowed[self.status]:
            raise ValueError(f"invalid run transition: {self.status.value} -> {target.value}")
        self.status = target
        return self.status
