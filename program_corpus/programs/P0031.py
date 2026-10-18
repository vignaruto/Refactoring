"""
Domain: String Processing & Text Analysis
Task: Check if string has balanced parentheses and brackets.
"""

def is_balanced_brackets(text: str) -> bool:
    stack = []
    pairs = {")": "(", "}": "{", "]": "["}
    for char in text:
        if char in "({[":
            stack.append(char)
        elif char in ")}]":
            if not stack or stack.pop() != pairs[char]:
                return False
    return len(stack) == 0

if __name__ == "__main__":
    assert is_balanced_brackets("{[()()]}") is True
    assert is_balanced_brackets("([)]") is False
