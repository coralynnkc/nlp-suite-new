# Tech Debt

Issues known but deliberately not fixed during the June 2026 overhaul, with
enough context to pick each one up later.

## Functional gaps

- **Six UI pages never call their agent endpoints.** The templates render forms
  but the views are GET-only, while the agent endpoints exist and work:
  `NER.html` → `/ner`, `boxplot.html` → `/boxplot`, `wordnet.html` → `/wordnet`,
  `gender_analysis.html` → (gender analysis), `shape_of_stories.html` → `/stories`,
  `excel_plotly_charts.html` → `/excel_charts`. Wiring them up means converting
  each view in `ui/app/views.py` to the `_proxy_post` helper and making the form
  field names match the endpoint's `Form()` parameters in `agent/src/main.py`.
- **Tips File feature removed, not replaced.** The web templates shipped broken
  "Tips File" buttons pointing at `tips_files.js` and `TIPS_*.pdf` assets that
  were never ported from the desktop app. The blocks were deleted (commit
  5de2ebe). The original PDFs live in the upstream NLP-Suite desktop repo if
  the feature is ever wanted back.

## Architecture

- **Flat sys.path imports.** `agent/src/main.py` adds every `agent/src/*`
  subdirectory to `sys.path`, and ~105 modules import each other by bare name.
  This defeats IDE navigation/refactoring and caused most of the 84 undefined-
  name bugs fixed in Phase 2. The right fix is converting `agent/src` into a
  real package with relative imports — large, mechanical, easy to get wrong;
  do it in one dedicated PR with no other changes.
  Related constraint: `Stanford_CoreNLP_util.py` imports the `corenlp_json_*`
  modules at its bottom, so those modules must not import it at module level
  (shared helpers live in `corenlp_json_common.py` instead).
- **Single-job concurrency by design.** The agent holds one `threading.Lock`;
  concurrent requests get 503. Fine for a single-researcher desktop tool, but
  any multi-user deployment needs a real job queue.

## Code quality

- **~129 inline TODO/FIXME comments** remain in `agent/src`, inherited from the
  research codebase (`grep -rn TODO agent/src`). They were left in place because
  most document genuine known limitations (chart column-format quirks, CoreNLP
  option handling, geocoding edge cases) rather than stale notes. Densest files:
  `gis/GIS_geocode_util.py`, `nlp/corenlp_json_syntax.py`, `charts/`.
- **Python 3.9 ceiling.** The agent image (ubuntu:20.04) runs Python 3.9, so
  3.10+ syntax (`X | None`, `zip(strict=)`, match statements) breaks at runtime.
  ruff `target-version = "py39"` in pyproject.toml guards lint suggestions, but
  nothing guards hand-written code; tests run on the host's newer Python and
  won't catch it. Consider a newer base image when upgrading the ML stack.

## Security / deployment

- **Django `SECRET_KEY` is hardcoded** in `ui/config/settings.py` (marked
  `django-insecure-`) and `DEBUG` defaults on. Acceptable for the local
  Docker-only research tool; must be env-injected before any hosted deployment.
- **CORS is wide open** (`allow_origins=["*"]`) on the agent. Same caveat.

## Testing

- **~20 of 26 agent endpoints have no tests** (covered: core utils, NER,
  wordnet, boxplot, excel charts, gender analysis*, shape of stories*;
  *integration-marked). The biggest gaps: sentiment, topic modeling, parse,
  word2vec, conll_table, svo, gis, wordcloud, ngrams, statistics.

## Forks (corenlp/, mallet/) — no code changes by policy

- `mallet/Dockerfile` installs unversioned `python3` + `fastapi`/`uvicorn`;
  `api.py` is live (serves `POST /run` on 5050 — do not delete).
- Heavy ML pins in `agent/requirements.txt` (torch 2.2.2, transformers 4.39.2,
  spacy 3.7.4) deliberately frozen; upgrading needs model-compatibility testing.
