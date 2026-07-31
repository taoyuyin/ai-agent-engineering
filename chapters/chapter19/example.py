"""Chapter 19: map a failure to an explicit repair decision."""

from reflection_runtime import Failure, RepairController


def main() -> None:
    controller = RepairController(max_retries=2)
    for failure in [
        Failure("TIMEOUT", "warehouse timeout"),
        Failure("INVALID_SCHEMA", "missing revenue"),
        Failure("PERMISSION_DENIED", "scope missing"),
    ]:
        print(failure.code, "=>", controller.decide("step-1", failure).action)


if __name__ == "__main__":
    main()
