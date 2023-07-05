Pattern matching is finally introduced into Python at Python 3.10. We consider a simplified version here.
In this version, only matching against constants is allowed, similar to `switch-case` in C.

Recall: Since our tool is about ambiguity at the parsing stage, all variables & constants are substituted with `id` in the grammar,
as they have been extracted by the lexer anyway.

```python
match status:
    case 400:
        return "Bad request"
    case 401:
        return "Unauthorized"
    case 403:
        return "Forbidden"
    case 404:
        return "Not found"
    case 418:
        return "I'm a teapot"
    case _:
        return "Something else"
```

Think about the following questions:

- What constraint should be used on the `case` clauses?
- What about the `match` clause?
- What is the relationship with respect to layout among all `case`s?
