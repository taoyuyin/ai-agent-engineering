"""Chapter 25: Knowledge Engineering

Production engineering checklist as Python data.
"""

CHECKLIST = ['知识组织', '知识生命周期', '更新', '治理', '知识质量']


def validate_system(enabled_items):
    missing = [item for item in CHECKLIST if item not in enabled_items]
    return {"ready": not missing, "missing": missing}


if __name__ == "__main__":
    print(validate_system(CHECKLIST[:3]))
