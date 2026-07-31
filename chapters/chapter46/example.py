"""Chapter 46: Enterprise Knowledge Agent

Enterprise scenario skeleton.
"""

SCENARIO = "Enterprise Knowledge Agent"
STEPS = ["background", "requirement", "architecture", "code", "launch", "lessons"]


def build_case_plan():
    return [{"step": step, "owner": "agent-engineering"} for step in STEPS]


if __name__ == "__main__":
    print(SCENARIO)
    for item in build_case_plan():
        print(item)
