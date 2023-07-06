# Artifact of paper "Automated Ambiguity Detection in Layout-Sensitive Grammars"

## Usage

We provide two approaches of building our prototype tool Lamb. Those familiar with the Nix package manager may directly use the nix flakes provided to build our tool. Otherwise, docker can be used to build Lamb (despite missing some functionalities), since we also provide a `Dockerfile` that wraps the installation of Nix package manager and the whole building process.

In short, we recommend building this project on a Unix-like OS with Nix. This is also the environment we used to develop this tool.

### Build with Nix package manager

#### Windows

**Note**: if you're a Windows user, please use WSL, and refer to the building guide for Unix-like operating systems.

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
nix run . -- tests/running-example/running-example.bnf
```

If you see "Ambiguous sentence of length 3 found." after a short while, it means the Lamb tool has been successfully built. Press Ctrl-D (Command-D on Mac) to exit Lamb, and read the next chapter to learn how to reproduce our experiment results.

### Build with Docker or Podman

It is also possible to build Lamb with Docker or Podman, though we *strongly recommend* using Nix due to its simplicity. In fact, our docker image also utilizes Nix internally to build the tool Lamb. Also, when using Docker, you lose the functionality of previewing parse trees on MacOS and Windows due to the lack of X11 server. Thus, we strongly recommend that you use Nix to build this project.

First built the image:

```bash
docker build -t lamb:0.0.0 .
```

Afterwards, run the lamb tool as follows:

```
docker run -v ./tests:/work/tests -it lamb:0.0.0 tests/running-example/running-example.bnf
```

If you see "Ambiguous sentence of length 3 found." after a short while, it means the Lamb tool has been successfully built. Press Ctrl-D (Command-D on Mac) to exit Lamb, and read the next chapter to learn how to reproduce our experiment results.

**Note:** if you're using Docker Desktop (or Podman Desktop) on MacOS or Windows, you may encounter problems with the last step when doing the bind-mount with `-v`. This is due to the fact that docker (or podman) runs in a virtual machine on those operating systems, and the VM has an independent filesystem. You may try to mount `/Users/` into that virtual machine ([docker file sharing](https://docs.docker.com/desktop/settings/mac/), [podman](https://stackoverflow.com/questions/70971713/mounting-volumes-between-host-macos-bigsur-and-podman-vm)), or use Nix to build instead.

-----

TODO: rewrite those below

### EBNF Format

The input of our grammar is in the EBNF format, with layout constraints introduced. We use the following symbols:

- `A|>` for offside on `A`
- `A>>` for offside-align on `A`
- `A~` for single on `A`
- `A || B` for `A` align `B`
- `A -> B` for `A` indent `B`
- `A |~ B` for `A` & `B` both having a starting token on the same line

You can check `tests/small-scale-2/2/final/2-2.bnf` for an example.

### Note on reproducing our results

As mentioned in our paper, our algorithm depends on a backend SMT solver. When solving an satisfiable formula, any of the possible models can be produced. However, different models can lead to different ambiguous sentences, which may lead to different disambiguating steps.

Empirically, most of the time Z3 gives the same model in a certain interaction round. In case a different model is found, our batch execution script (`run_tests.py`) will produce an error. This doesn't mean our tool failed, but only the fact that the emitted ambiguous sentence is not conforming to that recorded in our interaction configuration files. In that case, you need to check the output, and redo the round and all rounds that follows.

## Reproducing User Study

The grammars we used for this study are listed in `user-study/`. The raw data of user experiment is stored a database, and the metrics are calculated by the Jupyter notebook `user-study.ipynb`. To reproduce the data processing:

1. start the server by following "Running our tool with GUI support".
2. run the following commands:
```shell
host# cd dbdump
host# mongorestore dump/ mongodb://localhost:47017/
```
3. install dependencies with Pipenv on Python 3.10:
```shell
host# pipenv install
host# pipenv shell
```
4. start Jupyter, and use it to open the notebook.
```shell
host# jupyter lab
```

### User Study UI

To try the user study UI yourself, use the `docker-compose.yaml` file:
```shell
host# docker-compose build
host# docker-compose up -d
```
Then access http://localhost:8080 in your browser.

### User Survey

The data of the questionnaire is included in `user-study/questionnaire.csv`.
