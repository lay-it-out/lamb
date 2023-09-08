# Layout-sensitive AMBiguity detector

Detecting ambiguity of layout-sensitive grammars.

## Build

### Via Nix

```bash
nix build --no-link
```

Refer to [this guide](https://nixos.wiki/wiki/Flakes#Enable_flakes) in case you got error messages requesting enable the experimental features of Nix.

To enter a bash shell that provides an interactive build environment with all dependencies loaded, type:

```bash
nix develop
```

### Via Docker

First, build a Docker image with Nix inside:

```bash
docker build . -t lamb:0.0.2
```

Then, start a container using that image, so that you will be dropped into the Nix development shell:

```bash
docker run -it lamb:0.0.2
```

You should notice that the shell prompt now ends with `[lamb-dev]>`.

## Usage

In the Nix development shell (and project root directory), run `python -m lamb -h` to see help information. Some frequently used command-line toggles are listed below:

- `-c <length>`: stop searching for ambiguous sentences after reaching the given length. This is useful if you want to check the bounded unambiguity of a given grammar.
- `-l <length>`: start the checking process at the specified length. This assumes that one has already checked that any shorter sentence under this grammar is unambiguous.
- `-s`: output metrics like running time as well as REPL outputs as machine-readable JSON strings.

## A Tour of Lamb

In the Nix development shell, type the following command to run a small example:

```bash
python -m lamb tests/motivating-example.bnf
```

The file `motivating-example.bnf` defines a grammar for a toy imperative language, where a block is defined as a list of statements that are aligned with each other, where each statement is either an empty statement `nop` or a `do`-block that recursively takes a block as its body:

```
block ::= stmt|+|;
stmt  ::= "nop" | "do" block;
```

where notation `|+|` is the alignment version of Kleene plus: `stmt|+|` stands for a nonempty sequence of statements that are aligned to each other (i.e., with the same column number).

This grammar is indeed ambiguous:

```
...lines of solving process omitted...

***
Ambiguous sentence of length 3 found. It shall be listed below.
***

do
nop
nop

***
Found locally ambiguous variable: "new-var-0". It corresponds to token(s) [1, 3] in the ambiguous sentence.
***

NOTE: indexing for tokens in the sentence starts at 1. Spaces in the sentence are denoted as `␣'.
NEXT STEP: Review all parse trees using the following commands (execute line by line):

show tree new-var-0 0
show tree new-var-0 1

Type help for other available commands. Command completion available with TAB key.

Now entering REPL...

smt-ambig>
```

We see the shortest ambiguous sentence has a length of 3:

```
do
nop
nop
```

In the REPL, type `help` to see available commands:

```
smt-ambig> help
```

The command `show tree A tree-index` is used to display the (sub)trees rooted at nonterminal `A`. As hinted by the output, review the two parse trees of this ambiguous sentence:

```bash
smt-ambig> show tree new-var-0 0
smt-ambig> show tree new-var-0 1
```

The S-expression form will always be printed to the console; additionally, a figure will be opened (via `open` for Mac or `xdg-open` for Linux) if a preview application has been installed on your OS. Note that although the internal solver works on a binary normal form of the grammar, the trees are still in EBNF.

Try other commands as you wish and exit the REPL via the command `exit`.

## EBNF Syntax

This tool accepts `.bnf` files as inputs. A formal definition in Antlr can be found [here](lamb/ebnf/antlr/LayoutEBNF.g4).

Informally, a `.bnf` file consists of many production rules, each has the form

```
<nonterminal> ::= <expr> ;
```

The expression is one of the following:

- An identifier representing a nonterminal (e.g., `block`)
- A quoted string representing a terminal (e.g., `"do"`)
- A parenthesized expression (to promote priority)
- A sequence of expressions as concatenation
- A postfix expression
- An infix expression

We include all standard EBNF constructs:

- Postfix `+` for Kleene plus (occur at least once)
- Postfix `*` for Kleene star (occur an arbitrary number of times, including zero)
- Postfix `?` for optional (occur once or none)
- Infix `|` for alternative (choose either part)

We support the following layout constraints:

- Infix `<>` or `||` for alignment (the first tokens of the two parts have the same column number)
- Infix `->` for indentation (the second part has its first token to the right of the first part and a newline in between)
- Postfix `|>` for offside (any subsequent lines must start from a column that is further to the right of the start token of the first line)
- Postfix `|>>` for offside align (a variant of the above: subsequent lines can start from the same column as that of the first line)
- Postfix `|+|` for aligned Kleene plus (a variant of Kleene plus, but each element must be aligned to each other)
- Postfix `|*|` for aligned Kleene star (a variant of Kleene plus, but each element must be aligned to each other)
- Postfix `~` for single-line (one-line)

If needed, check the examples in `tests/` for a better understanding.

## Running Lamb on your own grammar

You might also be interested in running Lamb on a grammar you designed, rather than the grammars included as benchmarks.
Please first refer to the section "EBNF Syntax" to learn how to write your own grammar.
After that, launch the Nix development shell, and run Lamb as shown below:

```bash
python -m lamb ./path/to/your/grammar.bnf -c 20
```

As documented in section "Usage", `-c 20` ensures that the solver stops if no ambiguous sentence within 20 tokens is found.
Without this argument, the solver would run indefinitely on unambiguous grammars.

## Replication

This tool is a prototype implementation of the paper "Automated Ambiguity Detection in Layout-Sensitive Grammars". Check [this repo](https://github.com/lay-it-out/OOPSLA23-Artifact) for the replication package.

