"""Tool execution with input validation, bounded retry and normalized observations."""

from __future__ import annotations

from time import perf_counter

from pydantic import ValidationError

from framework.contracts import PlanStep, StepStatus, ToolObservation
from framework.tools import ToolDefinition


class ToolExecutor:
    def execute(
        self,
        step: PlanStep,
        tool: ToolDefinition,
        default_max_retries: int,
    ) -> ToolObservation:
        retries = step.max_retries if step.max_retries is not None else default_max_retries
        last_error: Exception | None = None

        for attempt in range(1, retries + 2):
            started = perf_counter()
            try:
                validated_input = tool.input_model.model_validate(step.call.arguments)
                data = tool.handler(validated_input)
                return ToolObservation(
                    step_id=step.step_id,
                    tool_name=tool.name,
                    status=StepStatus.COMPLETED,
                    data=data,
                    duration_ms=round((perf_counter() - started) * 1000, 3),
                    attempt=attempt,
                )
            except (ValidationError, ValueError, LookupError, RuntimeError) as error:
                last_error = error
                if attempt > retries:
                    return ToolObservation(
                        step_id=step.step_id,
                        tool_name=tool.name,
                        status=StepStatus.FAILED,
                        error=f"{type(error).__name__}: {error}",
                        duration_ms=round((perf_counter() - started) * 1000, 3),
                        attempt=attempt,
                    )

        raise AssertionError(f"unreachable executor state: {last_error}")
