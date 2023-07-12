# Lamb - tool for detecting ambiguation in layout-sensitive grammars

## Usage

We provide two approaches of building the prototype tool Lamb.
Those familiar with the Nix package manager may directly use the nix flakes provided to build our tool.
Otherwise, you can use the container provided in `Dockerfile`.

### Build with Nix package manager

#### Windows

**Note**: if you're a Windows user, please use the provided container.
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

You can also run `nix develop` first to drop yourself into the development shell.
You should notice that the shell prompt now ends with `[lamb-dev]>`.
Afterward, use `python -m lamb ./tests/motivating-example.bnf` to run the Lamb tool.

### Using Docker/Podman

First, build the image with the following command:

```bash
docker build . -t lamb:0.0.0
```

Then, start a container using that image, so that you will be dropped into the development shell:

```bash
docker run -it lamb:0.0.0
```

You should notice that the shell prompt now ends with `[lamb-dev]>`.
Inside the container, use `python -m lamb ./tests/motivating-example.bnf` to run the Lamb tool.