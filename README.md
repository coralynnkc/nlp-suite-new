# NLP Suite

A monorepo for running a suite of text-analysis tools through a browser UI. Designed for non-technical researchers: one command starts everything.

## Quick start

**Requirements:** Docker Desktop running, `git`, `bash`.

```bash
git clone https://github.com/coralynnkc/nlp-suite-new ~/nlp-suite-repo
cd ~/nlp-suite-repo
./start.sh
```

Opens `http://localhost:8000` automatically.

### File directories

All input and output files live outside the repo on your host machine:

| Directory               | Purpose                                    |
| ----------------------- | ------------------------------------------ |
| `~/nlp-suite/input/`    | Put corpus files here before running tools |
| `~/nlp-suite/output/`   | All tool output is written here            |
| `~/nlp-suite/csvInput/` | CSV input files (sentiment lexicons, etc.) |

To use a different base directory, set `NLP_SUITE_DIR` before running:

```bash
NLP_SUITE_DIR=/data/myproject ./start.sh
```

### Stopping

```bash
docker compose down
```

---

## Architecture

| Service   | What it does                 | Host port |
| --------- | ---------------------------- | --------- |
| `ui`      | Django web frontend          | 8000      |
| `agent`   | FastAPI processing backend   | 8080      |
| `corenlp` | Stanford CoreNLP (Java)      | 9000      |
| `mallet`  | MALLET topic modeling (Java) | 8081      |

The UI sends form submissions to the agent. The agent calls CoreNLP or MALLET when needed and writes output files to `~/nlp-suite/output/`.

Jobs run one at a time; submitting while a job is running returns "agent busy". After submitting, the status page shows a spinner, then either a completion message or the error that stopped the job (also logged in full: `docker compose logs agent`).

---

## Tools

| Tool                         | What it produces                                                      |
| ---------------------------- | --------------------------------------------------------------------- |
| File manager                 | Rename, copy, move, delete, split, filter corpus files                |
| Sentiment analysis           | VADER, ANEW, SentiWordNet, Hedonometer scores                         |
| Topic modeling               | LDA via Gensim, MALLET, or BERTopic                                   |
| Parsers & annotators         | POS tags, dependency parse, semantic roles (CoreNLP / spaCy / Stanza) |
| Word embeddings              | Word2Vec with t-SNE visualization                                     |
| CoNLL table analyzer         | Frequency analysis over parsed CoNLL output                           |
| Style analysis               | Readability indices, vocabulary complexity                            |
| SVO extraction               | Subject–Verb–Object triples                                           |
| N-grams & co-occurrences     | Frequency counts, co-occurrence search                                |
| File search                  | Keyword and dictionary search across corpus                           |
| Document statistics          | Token/type counts, corpus-level statistics                            |
| Sentence analysis            | Length, complexity, readability                                       |
| GIS                          | Location extraction and interactive map (Nominatim or Google Maps)    |
| Word clouds                  | Weighted word clouds with POS coloring                                |
| Sunburst / Sankey / Colormap | Hierarchical and flow visualizations                                  |
| NER                          | Named entity recognition (CoreNLP / spaCy / BERT)                     |
| WordNet                      | Semantic network graphs                                               |
| Gender analysis              | Name-based gender classification                                      |
| Shape of stories             | Narrative arc detection                                               |
| Excel/Plotly charts          | Interactive chart export                                              |
| Boxplot                      | Statistical boxplots                                                  |

---

## API keys (optional)

Enter keys on the UI settings page. They are saved to `~/nlp-suite/.env` on your host machine and never committed to the repo. See `.env.example` for the file format if you prefer to create it by hand.

| Key                   | Effect                                                       |
| --------------------- | ------------------------------------------------------------ |
| `GOOGLE_MAPS_API_KEY` | GIS tool uses Google Maps; falls back to Nominatim if absent |
| `NYT_API_KEY`         | Placeholder — no backend wiring yet                          |

---

## Development

```
agent/      FastAPI backend + NLP processing source
ui/         Django frontend
corenlp/    Stanford CoreNLP Docker container
mallet/     MALLET Docker container
start.sh    Start all services
```

### Running tests

```bash
cd agent && python -m pytest tests/ -v
```

Tests that require a live CoreNLP service are marked `@pytest.mark.integration` and skipped by default. To include them:

```bash
cd agent && python -m pytest tests/ -v -m integration
```

Test fixtures are in `agent/tests/fixtures/`.

### Linting

```bash
ruff check .
```

Note: the agent container runs Python 3.9 — avoid 3.10+ syntax in `agent/src/`. Known deferred issues live in [TECH_DEBT.md](TECH_DEBT.md).
