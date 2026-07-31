import unittest

from enterprise_runtime import AgentRequest, EnterpriseAgentRuntime


class EnterpriseRuntimeTest(unittest.TestCase):
    def test_returns_tenant_scoped_evidence(self) -> None:
        runtime = EnterpriseAgentRuntime()
        result = runtime.run(AgentRequest("1", "tenant-a", "u", "report", ("sales:read",)))
        self.assertEqual("completed", result["status"])
        self.assertEqual("sales_monthly", result["evidence"][0]["source"])

    def test_audits_denied_request(self) -> None:
        runtime = EnterpriseAgentRuntime()
        with self.assertRaises(PermissionError):
            runtime.run(AgentRequest("1", "tenant-a", "u", "report", ()))
        self.assertEqual("run_failed", runtime.audit.events[-1]["event"])


if __name__ == "__main__":
    unittest.main()
