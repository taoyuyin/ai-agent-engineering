import unittest

from lifecycle_runtime import AgentRun, LifecycleEngine, RunStatus


class LifecycleTest(unittest.TestCase):
    def test_happy_path(self) -> None:
        run = AgentRun("1", "goal")
        engine = LifecycleEngine()
        for status in (RunStatus.VALIDATING, RunStatus.PLANNING, RunStatus.RUNNING, RunStatus.COMPLETED):
            engine.transition(run, status, "ok")
        self.assertEqual(RunStatus.COMPLETED, run.status)

    def test_rejects_illegal_transition(self) -> None:
        with self.assertRaises(ValueError):
            LifecycleEngine().transition(AgentRun("1", "goal"), RunStatus.COMPLETED, "skip")

    def test_token_budget_terminates_run(self) -> None:
        run = AgentRun("1", "goal", max_tokens=10)
        engine = LifecycleEngine()
        engine.transition(run, RunStatus.VALIDATING, "ok")
        engine.record_model_usage(run, 8, 4)
        self.assertEqual(RunStatus.FAILED, run.status)
        self.assertEqual("token_budget_exhausted", run.events[-1]["reason"])


if __name__ == "__main__":
    unittest.main()
