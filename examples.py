# Normal statements

def normal_examples(a, b, c):
    x = a + b
    y = x * c
    print(y)


# Long statements

def long_statement_examples(a, b, c, d, e, f):
    result = a * b + c * d + e * f + a * c + b * d + c * e + d * f
    value = (a + b) * (c + d) - (e + f) * (a + c) + b * d


# Complex conditionals

def conditional_examples(a, b, c, d, e):
    if a > b and b > c and c > d and d > e:
        print("condition satisfied")

    if (a > b and c > d) or (d > e and a > e):
        print("another condition")


# Nested loops

def nested_loop_examples(n):
    for i in range(n):
        for j in range(n):
            print(i, j)

    for i in range(n):
        for j in range(n):
            for k in range(n):
                print(i, j, k)


# Multiple issues

def multiple_issue_examples(a, b, c, d, e, f, n):

    result = a * b + c * d + e * f + a * c + b * d + c * e

    if a > b and b > c and c > d and d > e:
        print("complex condition")

    for i in range(n):
        for j in range(n):
            print(i, j)

    return result