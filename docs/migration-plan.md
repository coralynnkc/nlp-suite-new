# Migration Plan

Goal: single monorepo, Docker + start.sh, web UI for non-technical researchers.

**Repo stats (scanned 2026-06-09):** 1,854 files · 336 directories · max nesting depth 6 · Python 347 files · HTML 40 · Markdown 16

---

## Phase 1 — Clone all repos (complete)

## Phase 2 — Restructure directories (complete)

## Phase 3 — Wire up 6 agent endpoints (complete)
All routes added to `agent/src/main.py`. Gender source files copied from `NLP-Suite/src/` to `agent/src/`.

| Endpoint | Source file |
|----------|-------------|
| `POST /ner` | `NER_main.py` |
| `POST /wordnet` | `knowledge_graphs_WordNet_main.py` |
| `POST /gender_analysis` | `html_annotator_gender_main.py` |
| `POST /shape_of_stories` | `shape_of_stories_main.py` |
| `POST /excel_plotly_charts` | `excel_plotly_charts.py` |
| `POST /boxplot` | `boxplot_chart.py` |

## Phase 4 — API key management
Settings page in UI with two fields:
- **Google Maps API key** — if set, `/gis` uses `GIS_Google_Maps_util.py`; otherwise falls back to Nominatim
- **NYT API key** — placeholder field, no backend wiring yet

Keys stored in local `.env`, never committed.

No `settings.html` template, no view, and no URL route exist in the UI. Phase 4 is entirely unstarted.

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

Neither `docker-compose.yml` nor `scripts/start.sh` exist yet. Individual `Dockerfile`s in each service dir are present.

## Phase 6 — Unit tests
- Framework: pytest
- Location: `agent/tests/`
- One test file per endpoint
- Fixtures: small `.txt` sample files in `agent/tests/fixtures/`
- No mocks for NLP logic — tests call real processing functions
- CoreNLP-dependent tests marked with `@pytest.mark.integration` and skipped unless CoreNLP service is up

Existing `test_*.py` files are colocated with source in `agent/src/` instead of `agent/tests/`. No `agent/tests/fixtures/` directory exists. Tests need to be moved and fixtures added.

---

## Tech debt

### `agent/src/main.py` — code issues
- **`gender_guesser` silently ignored** (line 481): the `/style_analysis` route accepts `gender_guesser` as a form param but immediately overrides it to `False`; the param is dead weight and confusing.
- **`outputDirectory` param accepted but overridden** (lines 158, 224, 307, etc.): every route hardcodes `~/nlp-suite/output` and discards the incoming value — the form field serves no purpose.
- **CORS wildcard** (line 34): `allow_origins=["*", ...]` — the `"*"` makes all specific origins redundant; tighten for production.
- **Commented-out error-handling block** (lines 55–63, 91–106): incomplete `app.worker_exception` design left in; either finish or remove.
- **`app.worker` not thread-safe**: the boolean flag is read and set without a lock; concurrent requests could race.

### Phase 2 — cleanup incomplete
- `daily/` empty stub directory still exists at repo root; should be deleted per plan

### Deferred — intentionally out of scope
| Source file | What it does | Reason deferred |
|-------------|-------------|-----------------|
| `knowledge_graphs_DBpedia_YAGO_main.py` | DBpedia/YAGO entity linking via SPARQL | External dependency, brittle API |
| `coreference_main.py` | Standalone coreference chain extraction | CoreNLP util migrated; standalone entrypoint deferred |
| `file_spell_checker_main.py` + utils | Spell checking pipeline | Files in `agent/src/` but no UI page or endpoint |
| Corpus profiler | Corpus-level statistics dashboard | No clear source file; was GUI-only |
| PCACE DB | Specialized database interface | External DB dependency |
| SENNA | Semantic role labeling via SENNA binary | External binary, Java-era tooling |
| TensorFlow semantic analysis | Deep learning sentiment/semantic pipeline | Heavy dependency, superseded by BERT tools |
