A simple let binding:

```fsharp
let id = id in id
```

A more complex example:

```fsharp
let id = id
    id = id
in  let id = id in id
```

Last example:

```fsharp
let id
       = id
            id
in id
```
