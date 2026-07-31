"""Chapter 29: Evaluation

Production engineering checklist as Python data.
"""

CHECKLIST = ['Offline', 'Online', 'Benchmark', '任务成功率', '质量评分']


def validate_system(enabled_items):
    missing = [item for item in CHECKLIST if item not in enabled_items]
    return {"ready": not missing, "missing": missing}


if __name__ == "__main__":
    print(validate_system(CHECKLIST[:3]))
