import unittest

from deployment_runtime import AgentService


class AgentServiceTest(unittest.TestCase):
    def setUp(self):
        self.service = AgentService("http://model", max_request_chars=30)

    def test_readiness_and_run_resource(self):
        self.assertFalse(self.service.health()["ready"])
        self.service.mark_ready()
        run = self.service.create_run({"tenant_id": "t1", "goal": "summarize"})
        self.assertEqual("queued", run["status"])
        self.assertEqual(run, self.service.get_run(run["run_id"]))

    def test_rejects_invalid_or_oversized_request(self):
        self.service.mark_ready()
        with self.assertRaises(ValueError):
            self.service.create_run({"goal": "x"})
        with self.assertRaises(ValueError):
            self.service.create_run({"tenant_id": "t", "goal": "x" * 31})

    def test_graceful_shutdown_stops_new_runs(self):
        self.service.mark_ready()
        self.service.begin_shutdown()
        self.assertFalse(self.service.health()["ready"])
        with self.assertRaises(RuntimeError):
            self.service.create_run({"tenant_id": "t", "goal": "x"})


if __name__ == "__main__":
    unittest.main()
