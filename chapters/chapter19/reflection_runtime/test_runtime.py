import unittest

from reflection_runtime import Failure, RepairController


class RepairTest(unittest.TestCase):
    def test_never_retries_permission_failure(self) -> None:
        decision = RepairController().decide("1", Failure("PERMISSION_DENIED", "no"))
        self.assertEqual("abort", decision.action)

    def test_exhausts_retry_budget(self) -> None:
        controller = RepairController(max_retries=1)
        self.assertEqual("retry", controller.decide("1", Failure("TIMEOUT", "x")).action)
        self.assertEqual("escalate", controller.decide("1", Failure("TIMEOUT", "x")).action)


if __name__ == "__main__":
    unittest.main()
