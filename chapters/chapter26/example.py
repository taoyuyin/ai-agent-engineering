"""Chapter 26: RAG

Production engineering checklist as Python data.
"""

CHECKLIST = ['Index', 'Chunk', 'Retrieve', 'Generate', '引用', '评测']


def validate_system(enabled_items):
    missing = [item for item in CHECKLIST if item not in enabled_items]
    return {"ready": not missing, "missing": missing}


if __name__ == "__main__":
    print(validate_system(CHECKLIST[:3]))
