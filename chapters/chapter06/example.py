"""Minimal tokenizer and token-budget MVP.

Run:
    python chapters/chapter06/example.py
"""

import re


MERGES = {
    ("A", "I"): "AI",
    ("A", "g"): "Ag",
    ("Ag", "e"): "Age",
    ("Age", "n"): "Agen",
    ("Agen", "t"): "Agent",
}


def basic_pieces(text):
    # Keep words and punctuation visible for teaching.
    return re.findall(r"[A-Za-z]+|[\u4e00-\u9fff]|[0-9]+|[^\s]", text)


def bpe_tokenize_word(word):
    pieces = list(word)
    changed = True
    while changed:
        changed = False
        index = 0
        new_pieces = []
        while index < len(pieces):
            pair = tuple(pieces[index:index + 2])
            if len(pair) == 2 and pair in MERGES:
                new_pieces.append(MERGES[pair])
                index += 2
                changed = True
            else:
                new_pieces.append(pieces[index])
                index += 1
        pieces = new_pieces
    return pieces


def tokenize(text):
    tokens = []
    for piece in basic_pieces(text):
        if piece.isascii() and piece.isalpha():
            tokens.extend(bpe_tokenize_word(piece))
        else:
            tokens.append(piece)
    return tokens


def fit_context(chunks, max_tokens):
    selected = []
    used = 0
    for chunk in chunks:
        token_count = len(tokenize(chunk))
        if used + token_count > max_tokens:
            continue
        selected.append(chunk)
        used += token_count
    return selected, used


if __name__ == "__main__":
    text = "AI Agent 可以调用工具，也需要管理上下文。"
    print("Text:", text)
    print("Tokens:", tokenize(text))

    chunks = [
        "差旅制度：高铁二等座可以报销。",
        "酒店标准：一线城市每天不超过 600 元。",
        "无关内容：" + "流程" * 20,
    ]
    selected, used = fit_context(chunks, max_tokens=30)
    print("\nSelected chunks:")
    for item in selected:
        print("-", item)
    print("Used tokens:", used)
