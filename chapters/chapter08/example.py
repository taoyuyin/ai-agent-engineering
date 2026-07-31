"""Chapter 8: Context

A small Python sketch for the chapter concept.
"""


def explain():
    concepts = ['Context Window', 'KV Cache', '上下文遗忘', '上下文选择', '上下文预算']
    for index, concept in enumerate(concepts, start=1):
        print(f"{index}. {concept}")


if __name__ == "__main__":
    explain()
