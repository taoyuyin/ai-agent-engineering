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


if __name__ == "__main__":
    unittest.main()
