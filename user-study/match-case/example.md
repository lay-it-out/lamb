`match` allows the user to do pattern-matching on algebraic data types.

Simple Example:

```fsharp
match id with
    | id -> id
    | id -> id
```

Another example:
```fsharp
match id with
    | id -> match id with
                | id -> id
                | id -> id
```

Counter-example (won't compile, line 2 is empty):
```fsharp
match id with

    | id -> id
```
