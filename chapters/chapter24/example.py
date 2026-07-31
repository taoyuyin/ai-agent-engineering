"""Chapter 24: Prompt Engineering

Production engineering checklist as Python data.
"""

CHECKLIST = ['Prompt Architecture', 'Prompt Version', 'Prompt Evaluation', '角色', '约束']


def validate_system(enabled_items):
    missing = [item for item in CHECKLIST if item not in enabled_items]
    return {"ready": not missing, "missing": missing}


if __name__ == "__main__":
    print(validate_system(CHECKLIST[:3]))
