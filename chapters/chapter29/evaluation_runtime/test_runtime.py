import unittest

from evaluation_runtime import AgentResult, EvalCase, EvaluationSuite


CASE = EvalCase("c1", ("approved",), ("policy.search",), True, 1000, 0.01)


class EvaluationSuiteTest(unittest.TestCase):
    def test_passes_complete_result(self):
        result = AgentResult("approved [p1]", ("policy.search",), ("p1",), 100, 0.001)
        report = EvaluationSuite(1.0).run([CASE], {"c1": result})
        self.assertTrue(report.released)
        self.assertEqual(1.0, report.pass_rate)

    def test_fails_wrong_tool_even_when_answer_is_correct(self):
        result = AgentResult("approved [p1]", ("web.search",), ("p1",), 100, 0.001)
        score = EvaluationSuite().score(CASE, result)
        self.assertFalse(score.passed)
        self.assertFalse(score.checks["tools"])

    def test_missing_result_fails_release_gate(self):
        report = EvaluationSuite(0.5).run([CASE], {})
        self.assertFalse(report.released)


if __name__ == "__main__":
    unittest.main()
