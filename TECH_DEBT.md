---
id: TECH_DEBT
aliases: []
tags: []
---

# Tech Debt

Issues known but deliberately not fixed during the June 2026 overhaul, with
enough context to pick each one up later. Entries are tagged by priority:
**P1** next up, **P2** worth a dedicated PR, **P3** fine to defer indefinitely.

**Next up:**
1. **[P2] Pyright type-checking** — wire pyright to resolve the `src` package
   (execution environment rooted at `agent/`, or `extraPaths: ["agent"]`) and fix
   the pre-commit hook's `rev: v1.1.x` tag to a concrete version. See Architecture.
2. **[P3] Everything else** — security hardening only matters for a hosted
   deployment; `iterrows()` vectorization only when an endpoint feels slow.

## UI/UX

- **[P2] Status page refresh gets stuck after a failed job.** `last_error` on
  the agent persists between jobs. A fresh visit to `/status` (e.g., after
  hitting browser refresh, or navigating back and resubmitting) polls once,
  sees `busy=false, last_error=<stale>`, and immediately renders the error
  banner — even though no new job has run. Two-part fix: (1) clear `last_error`
  at the start of the background thread in `agent/src/main.py` (before the job
  runs), so stale errors don't survive into the next request; (2) add a "Run
  another job" / back link to the `#failed` state in `ui/templates/status.html`
  so users aren't stranded without a navigation path.
- **[P2] Error messages are surfaced but rough.** Agent errors appear in two
  places: as a Django flash message on the form page (for 4xx/5xx or connection
  failures in `_proxy_post`) and in `#error-detail` on the status page (for
  background-job failures via `last_error`). Neither is styled prominently — the
  flash message blends into the page and `last_error` text is raw Python
  tracebacks. Improvement: dedicate a visible `.error-banner` component in the
  base template and truncate/format tracebacks on the status page (show the
  final exception line; add a "show full trace" toggle).
- **[P3] No progress bars.** All jobs run opaquely — the spinner runs until
  the agent reports `busy=false`. Adding per-job progress requires the backends
  to emit intermediate events (a `progress` field on `/status`, written by each
  `run_*` function at key checkpoints) and the status page to render a progress
  bar. This is meaningful scope because most `run_*` functions are single
  synchronous calls into utility modules with no natural checkpoint to hook.
  Worth revisiting if job runtimes become a UX pain point.

## Functional gaps

- **[P3] Gender analysis: US Social Security plot path is coming-soon.** The
  backend (`html_annotator_gender_main.py`) was ported June 2026 and the
  CoreNLP + dictionary annotation paths work via `POST /gender`, but the
  `plot_var` path needs the `lib/namesGender` data files
  (`SS_yearOfBirth.csv`, `SS_state_yearOfBirth.csv`, CMU/census name lists)
  that were never copied from the desktop repo. Copy them into
  `agent/lib/namesGender/` (where `GUI_IO_util.namesGender_libPath` points), re-enable
  the plot controls in `gender_analysis.html`, and stop hardcoding
  `plot_var=False` in the endpoint.
- **[P3] Non-Python wordcloud "services" just open external websites**
  (TagCrowd, Wordle, etc.), which a headless agent cannot do. The Python
  WordCloud backend itself was restored June 2026
  (`agent/src/analysis/wordclouds_util.py`, ported from the desktop repo).
  The external-service options in the wordclouds UI dropdown should either be
  removed or turned into plain links in the template.
- **[P3] Wordcloud image-mask options are coming-soon** (`prepareImage`,
  `usePNGFile`, `imageContour`, `useColorsForCsvColumns` in
  `wordclouds.html`): the `/wordcloud` endpoint accepts the params and the
  backend supports masks, but there is no image-upload workflow in the web UI.
  Same story for `manualCoreference` in `SVO.html` (needs an interactive
  split-screen editor) and `csv_file_var` in `NGrams_CoOccurrences.html`
  (needs a csv-file picker).
- **[P2] CoNLL table "all analyses" modules were never ported.** The seven
  `CoNLL_*_analysis_util` modules (clause, noun, adjective, ratio, adverb,
  verb, function-words) are imported inside `run_CoNLL_table_analyzer` but
  missing from `agent/src/nlp`, so `all_analyses_var=True` always raises
  ModuleNotFoundError (documented by `tests/test_conll_table.py`). The search,
  compute-sentence, and k-sentences paths work and are tested.
- **[P3] /gis csv-file input silently does nothing.** `GIS_main.py` passes the
  placeholder string `NER_StanfordCoreNLP_output` to `GIS_pipeline` instead of
  the selected csv file whenever `NER_extractor` is off, so the pipeline bails
  out on a nonexistent file (documented by `tests/test_gis.py`). The pipeline
  itself works when handed a real locations csv (that's how SVO calls it, and
  how the mocked-geocoder test exercises it). Related bugs found in the same
  sweep: `GIS_geocode_util.geocode:688` hits UnboundLocalError on `date` when
  the input has no Date column — confirmed against live CoreNLP + Nominatim,
  this breaks the *entire* `/gis` NER path for corpora without filename dates
  (the network-gated test in `tests/test_gis.py` is xfail-marked on it); and
  `GIS_main.py:88` calls `area_var.set(...)` (a tkinter remnant) on a plain
  string when the area value is malformed.
- **[P3] CoNLL k-sentences crashes on short documents.**
  `CoNLL_k_sentences_util.k_sent:181` truth-tests a pandas Series whenever a
  document has <= 2*K sentences (`ValueError: truth value of a Series is
  ambiguous`); fine for K=1 on real documents, but any short document kills
  the whole run (documented by `tests/test_conll_table.py`).
- **[P3] BERT_util is a partial port.** `BERT_util.py` now includes the upstream
  sentiment functions (ported June 2026) and `word_embeddings_BERT` (ported with
  the /word2vec backends — it only needs sentence-transformers/stanza/sklearn,
  already in the image). The upstream `NER_tags_BERT` and `doc_summary_BERT`
  depend on packages not in the agent image (`contextualSpellCheck`,
  `bert-extractive-summarizer`) and were not ported.
- **[P3] External-software install flow is desktop-era.** Algorithms needing
  external software (WordNet jars, Google Earth, …) used to launch the
  `NLP_setup_external_software_main.py` tkinter GUI, which does not exist in
  the agent; they now log a warning and return. A headless download path into
  `~/nlp-suite/external_software` would be needed to re-enable, e.g., the
  WordNet knowledge-graph endpoint (its test skips when the software is absent).
- **[P3] Tips File feature removed, not replaced.** The web templates shipped
  broken "Tips File" buttons pointing at `tips_files.js` and `TIPS_*.pdf`
  assets that were never ported from the desktop app. The blocks were deleted
  (commit 5de2ebe). The original PDFs live in the upstream NLP-Suite desktop
  repo if the feature is ever wanted back.

## Architecture

- **[P2] Pyright type-checking (next up).** Running pyright on the agent used to
  flood the output with false "import could not be resolved" errors because it
  resolves imports by package/path, not the old runtime `sys.path` munging. Now
  that `agent/src` is a real `src` package (relative imports throughout, run via
  `python -m src.main`), point pyright at it via an execution environment rooted
  at `agent/` (or `extraPaths: ["agent"]`) so `src.*` resolves. The pre-commit
  hook pinned to `rev: v1.1.x` won't install — pyright-python needs a concrete
  version (e.g. `v1.1.390`); fix the tag at the same time.
- **[P3] Import-cycle constraint.** `Stanford_CoreNLP_util.py` imports the
  `corenlp_json_*` modules at its bottom, so those modules must not import it at
  module level (shared helpers live in `corenlp_json_common.py` instead).
- **[P3] Single-job concurrency by design.** The agent holds one
  `threading.Lock`; concurrent requests get 503. Fine for a single-researcher
  desktop tool, but any multi-user deployment needs a real job queue.

## Code quality

- **[P3] ~129 inline TODO/FIXME comments** remain in `agent/src`, inherited
  from the research codebase (`grep -rn TODO agent/src`). They were left in
  place because most document genuine known limitations (chart column-format
  quirks, CoreNLP option handling, geocoding edge cases) rather than stale
  notes. Densest files: `gis/GIS_geocode_util.py`, `nlp/corenlp_json_syntax.py`,
  `charts/`.
- **[P3] Python 3.9 ceiling.** The agent image (ubuntu:20.04) runs Python 3.9,
  so 3.10+ syntax (`X | None`, `zip(strict=)`, match statements) breaks at
  runtime. ruff `target-version = "py39"` in pyproject.toml guards lint
  suggestions, but nothing guards hand-written code; tests run on the host's
  newer Python and won't catch it. Consider a newer base image when upgrading
  the ML stack.

## Performance

- **Model-load caching: fixed June 2026** via `agent/src/core/model_cache.py`
  (process-wide dict keyed by model args; stanza/spaCy/SentenceTransformer
  getters). Residuals not converted: `Stanza_functions_util.py` builds its
  module-level `stanzaPipeLine` at import time (already once-per-process, but
  it loads even for jobs that never use it — could become lazy via the cache),
  and `file_spell_checker_util.py`'s `MultilingualPipeline()` calls.
- **[P3] Pervasive `df.iterrows()`/row-append loops** (~31 sites) inherited
  from the research code. Vectorizing is per-algorithm work; only worth it for
  the endpoints that feel slow in practice.

## Security / deployment (defer until any hosted deployment)

- **[P3] Django `SECRET_KEY` is hardcoded** in `ui/config/settings.py` (marked
  `django-insecure-`) and `DEBUG` defaults on. Acceptable for the local
  Docker-only research tool; must be env-injected before any hosted deployment.
- **[P3] CORS is wide open** (`allow_origins=["*"]`) on the agent. Same caveat.

## Testing

- **[P3] ~10 of 24 agent endpoints still have no tests** (covered as of June
  2026: core utils, model cache, NER, wordnet*, boxplot, excel charts,
  wordcloud, sentiment, topic modeling (Gensim), ngrams, gender analysis*,
  shape of stories*, parse*, word2vec*, conll_table, svo*, gis*, statistics;
  *some paths integration-, network-, or external-software-gated). Remaining:
  file_manager, style_analysis, sunburst, colormap, sankey, file_search,
  sentence_analysis, settings — all small enough to defer. Tests skip on the
  host (heavy deps live in the Docker image); run them in the agent container:
  `docker run --rm -v "$PWD/agent:/work" -w /work nlp-suite-agent python3.9 -m pytest tests/`
  For CoreNLP-gated tests, run on the compose network with
  `--network nlp-suite_nlp-suite-network -e CORENLP_URL=http://corenlp:9000`
  and `-m integration`; Nominatim-gated GIS tests need `NLP_SUITE_TEST_NETWORK=1`.
  The three /word2vec backend tests (Gensim, WSI, BERT) download models on first
  run and are gated behind `NLP_SUITE_TEST_BERT=1`; the guard-path tests run
  unconditionally.
- **[P3] MALLET topic modeling has no hermetic test.** The mallet service
  reads its own mounted `/app/input` (the live `~/nlp-suite/input`), so a
  test would touch real user data. The BERTopic path and roBERTa sentiment
  are testable but gated behind `NLP_SUITE_TEST_BERT=1` (large HuggingFace
  model downloads on first run).

## Forks (corenlp/, mallet/) — no code changes by policy

- `mallet/Dockerfile` installs unversioned `python3` + `fastapi`/`uvicorn`;
  `api.py` is live (serves `POST /run` on 5050 — do not delete).
- Heavy ML pins in `agent/requirements.txt` (torch 2.2.2, transformers 4.39.2,
  spacy 3.7.4) deliberately frozen; upgrading needs model-compatibility testing.
