# Artifact of paper "Automated Ambiguity Detection in Layout-Sensitive Grammars"

## Usage

We provide two approaches of building our prototype tool Lamb. Those familiar with the Nix package manager may directly use the nix flakes provided to build our tool. Otherwise, you can use the packaged virtual machine, which runs NixOS and contains our tool.

### Build with Nix package manager

#### Windows

**Note**: if you're a Windows user, please use the provided virtual machine to complete the artifact evaluation process.

#### Unix-like OS (Linux / MacOS)

If you're using Linux distributions other than NixOS (like Ubuntu, Fedora or Archlinux), install Nix package manager first. Skip this step if you already have Nix installed. Nix is usually packaged by your distribution, but the packaged version might not be new enough. Therefore, we suggest using the [installer](https://zero-to-nix.com/concepts/nix-installer) provided by Determinate Systems by running the following command:

```bash
curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install
```

Afterwards, set your current directory to the artifact directory (`lamb-artifact`) and run the following to build the artifact:

```bash
nix build
```

The building process should take no more than 15 minutes. If an error occurs asking you to enable experimental features of nix, refer to [this guide](https://nixos.wiki/wiki/Flakes#Enable_flakes) to enable flakes and nix commands.

As the building process is now complete, you may run the Lamb tool on a small example provided by us:

```bash
nix run . -- tests/motivating-example.bnf
```

If you see "Ambiguous sentence of length 3 found." after a short while, it means the Lamb tool has been successfully built. Press Ctrl-D (Command-D on Mac) to exit Lamb, and read the next chapter to learn how to reproduce our experiment results.

### Using the Virtual Machine

Located in the folder `vm` is the virtual machine we provided, which includes NixOS, our code and the running environment. This is the preferred method if your operating system is not officially supported by Nix. To use the provided VM, please import the provided VirtualBox Appliance file into VirtualBox, boot the virtual machine, and launch Konsole (the terminal emulator). The easiest way of launching Konsole is clicking the rightmost icon on the taskbar. The `lamb-artifact` folder is located at `/home/demo/Desktop/lamb-artifact`. Switch into that folder using `cd` command, and refer to the last section for next step instructions.

## Running our tool

### Introduction to EBNF Format with layout constraints

The input of our grammar is in the EBNF format, with layout constraints introduced. We use the following symbols:

- `A|>` for offside on `A`
- `A>>` for offside-align on `A`
- `A~` for single on `A`
- `A || B` for `A` align `B`
- `A -> B` for `A` indent `B`

You can check `tests/motivating-example.bnf` to see the usage of those symbols.

### Motivating example

The file `tests/motivating-example.bnf` contains the grammar used in Section 2 of the paper. First, run our tool on that grammar (assuming that your current directory is `lamb-artifact`):

```
nix run . -- tests/motivating-example.bnf
```

The output should look like below

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
NEXT STEP: List and review all parse trees. Type help for available commands. Command completion available with TAB key.

Now entering REPL...
smt-ambig>
```

This indicates that our tool successfully found an ambiguous sentence:

```
do
nop
nop
```

As mentioned in the paper, we only consider dissimilar subtrees, since this (in combination with the reachability condition) is logically equivalent to derivation ambiguity. Considering the dissimilar subtrees that witnesses local ambiguity, two of them exists for the subword $w^{1\dots3}$, and they both has the variable $\text{new-var-0}$ as their root. $\text{new-var-0}$ is a new variable created in the process of translating EBNF grammar into LS2NF grammar. When presenting the parse trees, this transformation is undone -- you'll only see variables and rules in original EBNF grammar in the presented parse trees.

First, type `list tree new-var-0` and press enter to ensure that there exists two parse trees for the given sentence:

```
smt-ambig> list tree new-var-0
Parse trees of nonterminal: new-var-0
+-------+---------------------+
| index |         type        |
+-------+---------------------+
|   0   | UnaryExpressionNode |
|   1   | UnaryExpressionNode |
+-------+---------------------+
```

Please pay attention to how the common tree root $\text{new-var-0}$ is used in the command to denote the parse tree forest.

Then, have a look at the parse trees one by one, by using the commands `show tree new-var-0 0` and `show tree new-var-0 1`.  Press enter after each command. You should see the parse trees generated by our tool Lamb.

Finally, input `exit	` to quit our tool.

### Reproducing the evaluation results

We assume that you are currently at the `lamb-artifact` folder. First, load the development shell for our tool:

```bash
nix develop
```

Then, execute the following command to run all but Python / SASS testcases.

```bash
python run_tests.py
```

This shall take around 10-25 minutes. Afterwards, the total running time (sum of `solve_time` and `other_time`), ambiguous sentence length, among other details, shall be printed to the terminal. Another copy will also be stored into `result.json` in the current folder.

To run every testcases including Python and SASS, please run the following command.

```bash
python run_tests.py --all
```

Note that this can take very long (>24h) to complete.
