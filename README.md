# Artifact of Lay-it-out

TODO: usage of nix

This folder contains the source code of our prototype tool lay-it-out with the evaluation data and scripts for the two case studies and the user study.

## Usage

It is recommended to build via Docker (or other compatible container environment). To distinguish container and host shells, we use the prompt `host#` and `container#` respectively in the following.

## Reproducing Case Studies

Build the docker image first:
```shell
host# docker build .
```
This command will grab all required libraries and tools like ANTLR, Z3, etc. Depending on your network, the command above can take a while.

If the build successfully completes, you will be presented an sha256 hash of the image.
Start a container with that image:
```shell
host# docker run -it <image-id> bash # replace <image-id> with the sha256 hash from last command.
```

In the container shell, you can first run some simple testcases to identify if the environment is working normally:
```shell
container# cd /opt/smt-disambig
container# python run_tests.py --simple
```
Note that due to the randomness of SMT solver, the produced results can be totally different from that on our machine. See section "Note on reproducing our results" for more details.

To reproduce the two case studies, run
```shell
container# python run_tests.py
```
Results will be recorded in `result.json`.

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
