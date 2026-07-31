"""Minimal self-attention MVP.

Run:
    python chapters/chapter05/example.py

This is intentionally tiny and dependency-free. It demonstrates the core
idea: each token builds its new representation by attending to other tokens.
"""

import math


TOKENS = ["profit", "declined", "because", "inventory"]

# Tiny hand-written embeddings: [business_metric, negative_change, cause, operations]
EMBEDDINGS = {
    "profit": [1.0, 0.0, 0.0, 0.2],
    "declined": [0.8, 1.0, 0.0, 0.0],
    "because": [0.0, 0.2, 1.0, 0.0],
    "inventory": [0.2, 0.0, 0.8, 1.0],
}


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def softmax(scores):
    max_score = max(scores)
    exps = [math.exp(score - max_score) for score in scores]
    total = sum(exps)
    return [value / total for value in exps]


def weighted_sum(weights, vectors):
    return [
        round(sum(weight * vector[i] for weight, vector in zip(weights, vectors)), 3)
        for i in range(len(vectors[0]))
    ]


def self_attention(tokens):
    vectors = [EMBEDDINGS[token] for token in tokens]
    outputs = {}
    for token, query in zip(tokens, vectors):
        scores = [dot(query, key) / math.sqrt(len(query)) for key in vectors]
        weights = softmax(scores)
        outputs[token] = {
            "attention": {
                other: round(weight, 3) for other, weight in zip(tokens, weights)
            },
            "new_representation": weighted_sum(weights, vectors),
        }
    return outputs


if __name__ == "__main__":
    for token, result in self_attention(TOKENS).items():
        print(f"\nToken: {token}")
        print("Attention:", result["attention"])
        print("New representation:", result["new_representation"])
