"""Chapter 9: Reasoning

A small Python sketch for the chapter concept.
"""


def explain():
    concepts = ['CoT', 'ReAct', 'ToT', 'Reflection', 'Reasoning Model']
    for index, concept in enumerate(concepts, start=1):
        print(f"{index}. {concept}")


if __name__ == "__main__":
    explain()
