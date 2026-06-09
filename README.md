# NLP Suite

A monorepo for running a suite of text-analysis tools through a browser UI. Designed for non-technical researchers: one command starts everything.

## Quick start

```bash
./scripts/start.sh
```

Opens `http://localhost:8000` automatically.

**Requirements:** Docker Desktop running.

## Architecture

| Service | What it does | Port |
|---------|-------------|------|
| `ui` | Django web frontend | 8000 |
| `agent` | FastAPI processing backend | 8080 |
| `corenlp` | Stanford CoreNLP (Java) | 9000 |
| `mallet` | MALLET topic modeling (Java) | 8081 |

The UI sends form submissions to the agent. The agent calls CoreNLP or MALLET when needed and writes output files to `~/nlp-suite/output/`.

## Tools available

| Tool | What it produces |
|------|-----------------|
| File manager | Rename, copy, move, delete, split, filter corpus files |
| Sentiment analysis | VADER, ANEW, SentiWordNet, Hedonometer scores |
| Topic modeling | LDA via Gensim, MALLET, or BERTopic |
| Parsers & annotators | POS tags, dependency parse, semantic roles (CoreNLP / spaCy / Stanza) |
| Word embeddings | Word2Vec with t-SNE visualization |
| CoNLL table analyzer | Frequency analysis over parsed CoNLL output |
| Style analysis | Readability indices, vocabulary complexity |
| SVO extraction | Subject–Verb–Object triples |
| N-grams & co-occurrences | Frequency counts, co-occurrence search |
| File search | Keyword and dictionary search across corpus |
| Document statistics | Token/type counts, corpus-level statistics |
| Sentence analysis | Length, complexity, readability |
| GIS | Location extraction and interactive map (Nominatim or Google Maps) |
| Word clouds | Weighted word clouds with POS coloring |
| Sunburst / Sankey / Colormap | Hierarchical and flow visualizations |
| NER *(in progress)* | Named entity recognition (CoreNLP / spaCy / BERT) |
| WordNet *(in progress)* | Semantic network graphs |
| Gender analysis *(in progress)* | Name-based gender classification |
| Shape of stories *(in progress)* | Narrative arc detection |
| Excel/Plotly charts *(in progress)* | Interactive chart export |
| Boxplot *(in progress)* | Statistical boxplots |

## API keys (optional)

Enter keys in the UI settings page. They are saved to `.env` at the repo root and never committed.

| Key | Effect |
|-----|--------|
| `GOOGLE_MAPS_API_KEY` | GIS tool uses Google Maps; falls back to Nominatim if absent |
| `NYT_API_KEY` | Placeholder — no backend wiring yet |

## Output

All output files are written to `~/nlp-suite/output/` on the host machine.

## Development

```
agent/      FastAPI backend + NLP processing source
ui/         Django frontend
corenlp/    Stanford CoreNLP Docker container
mallet/     MALLET Docker container
docs/       Migration plan and functionality audit
```

See [`docs/migration-plan.md`](docs/migration-plan.md) for current status and remaining work.
