"""Chapter 27: Semantic Layer

Production engineering checklist as Python data.
"""

CHECKLIST = ['企业数据语义', '指标', '维度', '口径', '权限', 'Data Agent']


def validate_system(enabled_items):
    missing = [item for item in CHECKLIST if item not in enabled_items]
    return {"ready": not missing, "missing": missing}


if __name__ == "__main__":
    print(validate_system(CHECKLIST[:3]))
