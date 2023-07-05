The `with` statement is used with context managers, i.e., objects with `__enter__` and `__exit__` methods declared. A common case of using `with` is handling open files:

```python
with open('1.txt') as f:
    # now f is open, do something with if
    print(f.read())
# now we're out of with-block, and f is automatically closed
print('done!')
```

Another scenario of using it is for suppressing some kinds of exceptions, utilizing `contextlib`.

```python
# took from docs.python.org
import os
from contextlib import suppress

with suppress(FileNotFoundError):
    os.remove('somefile.tmp')  # a FileNotFoundError here is acceptable...
    os.remove('somefile2.tmp') # also here..
os.remove('secrets.tmp')       # but not here! (this statement is not guarded by `with`)
```

### Layout Constraints

One thing you might have noticed is that "every statement is starting at the same column", that is,
horizontally aligned on their left. Another requirement is that only statements "more indented" from the "with" keyword will belong to the with block.

We then introduce several symbols. Those symbols are added to EBNF grammars to ensure
extra constraints.

- Aligned $\parallel$: Binary operator; both sides start at the same column.
  Consider $S \to A \parallel B, A \to "pass", B \to "pass"$.
  ```python
  pass # aligned, contained in the language
  pass
  ```
  ```python
      pass # not aligned, not contained in the language
  pass
  ```
- Indented ◫ (also written as `->`): Binary operator; for an expression like $A$ ◫ $B$, it is required that 
  - the first token yielded by $B$ is on the next line of the last token yielded by $A$;
  - the first token yielded by $B$ is on the right of the first token yielded by $A$.
  - Examples follow. $S \to A$ ◫ $B, A \to wx, B \to yz$.
    - The sentences below all belong to $\mathcal{L}(S)$:
      ```
      w
        x
        y z
      ```
      ```
      w
      x
            y z
      ```
      ```
      w x
        y z
      ```
    - However, the ones below aren't in $\mathcal{L}(S)$:
      ```
      w x
      y z
      ```
      ```
      w x

        y z
      ```
      (⬆extra empty line: line 2)
- Offside ${}^\rhd$ (also written as `|>`): Unary operator; $(A)^\rhd$ ensure that the offside rule holds, i.e., all tokens following the first one yielded from $A$ is to its right side. Consider $S \to (w^{+})^\rhd$; the following are all in its language:
  ```
  w w w
  ```
  ```
  w
   w w
  ```
  ```
  w w w w
   w w w
  ```
- Same line ⦇$\cdot$⦈ (also written as `~`): Unary operator; when applied on a expression,
  all tokens in its yield are laid on the same line. Consider $S \to$ ⦇ $abcd$ ⦈, we have 2 sentences:
  ```
  a b c d
  ```
  and 
  ```
  a b
  c d
  ```
  Only the first is in $\mathcal{L}(S)$.

### Extensions of Kleen Star / Plus

In EBNF, we have Kleene Star & Kleene Plus. Those operators are shorthand for recursive reference on nonterminals. Take $S \to {A}^{+}$ as an example. It is equivalent to: $S \to SA \mid A$.

Naturally we can also introduce "aligned" versions of those symbols. $S \to {A}^{+}$ means $S \to (S \parallel A) \mid A$, and $S \to {A}^{*}$ means $S \to (S \parallel A) \mid \epsilon$.


### Misc

- The first nonterminal in the EBNF file is considered the root of grammar.
- Since our tool is about ambiguity at the parsing stage, all variables & constants are substituted with `id` in the grammar, as they have been extracted by the lexer anyway.