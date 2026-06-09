# Migration Plan

Goal: single monorepo, Docker + start.sh, web UI for non-technical researchers.

---

## Phase 1 — Clone all repos (complete)
All six repos committed to monorepo with `.git` removed from each.

## Phase 2 — Restructure directories
Move content into the agreed target layout:

| From | To | Notes |
|------|----|-------|
| `nlp-suite-agent/` | `agent/` | FastAPI backend |
| `nlp-suite-ui/` | `ui/` | Django frontend |
| `stanford-corenlp-docker/` | `corenlp/` | Java container |
| `MALLET-docker/` | `mallet/` | Java container |
| `NLP-Suite/` | `NLP-Suite/` | Keep as reference |
| `nlp-suite-runner/` | delete | Replaced by start.sh |
| `agent/`, `ui/`, `corenlp/`, `mallet/`, `daily/` (empty stubs) | delete | |

## Phase 3 — Wire up 6 missing agent endpoints
All source logic exists in `NLP-Suite/src/`. Wrap each in a FastAPI route.

| Endpoint | Source file | CoreNLP needed? |
|----------|-------------|----------------|
| `POST /ner` | `NER_main.py`, `BERT_util.py` | Yes (optional: spaCy/Stanza fallback) |
| `POST /wordnet` | `knowledge_graphs_WordNet_main.py` | No (NLTK WordNet) |
| `POST /gender_analysis` | `html_annotator_gender_main.py` | No (gender-guesser) |
| `POST /shape_of_stories` | `shape_of_stories_main.py` | No (sentiment + sklearn) |
| `POST /excel_plotly_charts` | `charts_Excel_main.py` | No (Plotly, openpyxl) |
| `POST /boxplot` | `charts_matplotlib_seaborn_util.py` | No (matplotlib/seaborn) |

## Phase 4 — API key management
Settings page in UI with two fields:
- **Google Maps API key** — if set, `/gis` uses `GIS_Google_Maps_util.py`; otherwise falls back to Nominatim
- **NYT API key** — placeholder field, no backend wiring yet
Keys stored in local `.env`, never committed.

## Phase 5 — Docker + start.sh
`docker-compose.yml` at repo root coordinates four services:

| Service | Dockerfile | Port |
|---------|-----------|------|
| `agent` | `agent/Dockerfile` | 8080 |
| `ui` | `ui/Dockerfile` | 8000 |
| `corenlp` | `corenlp/Dockerfile` | 9000 |
| `mallet` | `mallet/Dockerfile` | 8081 |

`scripts/start.sh`:
1. Check Docker is running
2. `docker compose up -d`
3. Wait for health checks
4. Open browser to `http://localhost:8000`

## Phase 6 — Unit tests
- Framework: pytest
- Location: `agent/tests/`
- One test file per endpoint
- Fixtures: small `.txt` sample files in `agent/tests/fixtures/`
- No mocks for NLP logic — tests call real processing functions
- CoreNLP-dependent tests marked with `@pytest.mark.integration` and skipped unless CoreNLP service is up
