# Layout-sensitive AMBiguity detector

Detecting ambiguity of layout-sensitive grammars.

## Build

### Via Nix

```bash
nix build --no-link
```

Refer to [this guide](https://nixos.wiki/wiki/Flakes#Enable_flakes) in case you got error messages requesting enable the experimental features of Nix.

Enter a bash shell that provides an interactive build environment with all dependencies loaded via `nix develop`.

### Via Docker

First, build a Docker image with Nix inside:

```bash
docker build . -t lamb:0.0.0
```

Then, start a container using that image, so that you will be dropped into the Nix development shell:

```bash
docker run -it lamb:0.0.0
```

You should notice that the shell prompt now ends with `[lamb-dev]>`.

## Usage

In the Nix development shell (and project root directory), run `python -m lamb -h` to see help information.

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

This grammar is indeed ambiguous: our tool outputs the following that presents a shortest ambiguous sentence found:

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

## Replication

This tool is a prototype implementation of the paper "Automated Ambiguity Detection in Layout-Sensitive Grammars". Check [this repo](https://github.com/lay-it-out/OOPSLA23-Artifact) for the replication package.