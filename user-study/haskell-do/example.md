`do` block combines multiple monads together.

Two top-level statements: `putStrLn id` and `main = ...`:
```haskell
putStrLn id
main = do putStrLn id
          putStrLn id
```

Two statements in `do`-block:
```haskell
main 
  = do putStrLn
                id
       putStrLn id
```

Only 1 statement in `do`-block:
```haskell
main = do
         putStrLn id
```