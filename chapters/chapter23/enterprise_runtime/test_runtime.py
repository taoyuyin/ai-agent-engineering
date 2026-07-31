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

    def test_retrieval_is_tenant_scoped_and_versioned(self) -> None:
        runtime = EnterpriseAgentRuntime()
        result = runtime.run(
            AgentRequest("1", "tenant-a", "u", "销售指标与规则", ("sales:read",))
        )
        self.assertEqual("hash-embedding-v1", result["embedding_model"])
        self.assertNotIn("tenant-b", result["context"])
        self.assertTrue(any(event["event"] == "context_compiled" for event in runtime.audit.events))


if __name__ == "__main__":
    unittest.main()
