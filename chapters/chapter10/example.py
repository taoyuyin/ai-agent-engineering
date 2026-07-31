"""Chapter 10: Function Calling

A small Python sketch for the chapter concept.
"""


def explain():
    concepts = ['Tool Calling', 'Structured Output', 'JSON Schema', '参数校验', '执行闭环']
    for index, concept in enumerate(concepts, start=1):
        print(f"{index}. {concept}")


if __name__ == "__main__":
    explain()
