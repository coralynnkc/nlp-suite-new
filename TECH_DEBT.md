# Tech Debt

Issues deliberately deferred during the June 2026 overhaul. Tags: **P1** next up, **P2** worth a dedicated PR, **P3** fine to defer indefinitely. Fix one entry per PR (see CLAUDE.md).

**Next up:** **[P3] Everything else** — security hardening only matters for a
hosted deployment; `iterrows()` vectorization only when an endpoint feels slow.

## UI/UX

- **[P3] No progress bars.** Jobs run opaquely until `busy=false`. Needs `run_*`
  functions to emit a `progress` field on `/status` at checkpoints (most are
  single synchronous calls with no natural hook) and a bar on the status page.

## Functional gaps

- **[P2] CoNLL "all analyses" modules never ported.** The seven
  `CoNLL_*_analysis_util` modules (clause, noun, adjective, ratio, adverb, verb,
  function-words) are imported in `run_CoNLL_table_analyzer` but missing from
  `agent/src/nlp`, so `all_analyses_var=True` raises ModuleNotFoundError
  (`tests/test_conll_table.py`). Search / compute-sentence / k-sentences work.
- **[P3] Gender US Social Security plot path coming-soon.** `plot_var` needs
  `lib/namesGender` data files (`SS_yearOfBirth.csv`, `SS_state_yearOfBirth.csv`,
  CMU/census name lists) never copied from desktop. Copy into
  `agent/lib/namesGender/`, re-enable plot controls in `gender_analysis.html`,
  stop hardcoding `plot_var=False`. CoreNLP + dictionary paths work.
- **[P3] Non-Python wordcloud "services" open external websites** (TagCrowd,
  Wordle) a headless agent can't reach. Remove them or make them plain links in
  `wordclouds.html`. The Python WordCloud backend works.
- **[P3] Coming-soon UI workflows.** Wordcloud image-mask options (`prepareImage`,
  `usePNGFile`, `imageContour`, `useColorsForCsvColumns` in `wordclouds.html`)
  need an image-upload flow; `manualCoreference` in `SVO.html` needs a
  split-screen editor; `csv_file_var` in `NGrams_CoOccurrences.html` needs a csv
  picker. Backends/endpoints already accept the params.
- **[P3] /gis csv-file input does nothing.** `GIS_main.py` passes placeholder
  `NER_StanfordCoreNLP_output` to `GIS_pipeline` when `NER_extractor` is off, so
  it bails on a nonexistent file (`tests/test_gis.py`). Related:
  `GIS_geocode_util.geocode:688` UnboundLocalError on `date` when there's no Date
  column breaks the whole `/gis` NER path for corpora without filename dates
  (xfail-marked); `GIS_main.py:88` calls tkinter remnant `area_var.set(...)` on a
  string when the area is malformed. Pipeline works with a real locations csv.
- **[P3] CoNLL k-sentences crashes on short documents.**
  `CoNLL_k_sentences_util.k_sent:181` truth-tests a pandas Series when a doc has
  <= 2\*K sentences (`ValueError: truth value of a Series is ambiguous`); fine for
  K=1 on real docs (`tests/test_conll_table.py`).
- **[P3] BERT_util partial port.** Sentiment + `word_embeddings_BERT` ported.
  `NER_tags_BERT` and `doc_summary_BERT` need packages not in the image
  (`contextualSpellCheck`, `bert-extractive-summarizer`).
- **[P3] External-software install flow desktop-era.** Algorithms needing external
  software (WordNet jars, Google Earth) used to launch the
  `NLP_setup_external_software_main.py` tkinter GUI; they now log a warning and
  return. Re-enabling (e.g. the WordNet KG endpoint) needs a headless download
  path into `~/nlp-suite/external_software`.
- **[P3] Tips File feature removed** (commit 5de2ebe) — broken buttons pointing at
  unported `tips_files.js`/`TIPS_*.pdf`. Original PDFs in the upstream desktop
  repo if wanted back.

## Architecture

- **[P3] ~1030 legacy `agent/src` pyright findings.** Standard-mode findings from
  research code (`reportPossiblyUnbound` ~400, `reportArgumentType` ~220,
  `reportAttributeAccessIssue` ~150, optional/call/operator). Not fixed (wire-up
  only); the blocking pre-commit hook surfaces them per-file on touch (boy-scout
  cleanup). Pyright runs in pre-commit only, not CI (`lint.yml` is ruff-only) —
  it can't gate until this backlog is at zero or baselined, else every PR fails.
  Once cleared, add a pyright step to `lint.yml` so contributors without hooks
  installed don't bypass the check.
- **[P3] `ui/` not type-checked.** Django app code excluded from pyright (would
  need `ui/.venv` or stubs via a second `executionEnvironments` root /
  `venvPath`); 11 unresolved-`django.*` errors.
- **[P3] 3 stray bare lazy-imports** hidden by pyright `reportMissingImports:
none`: `import IO_string_util` (`analysis/NGrams_CoOccurrences_util.py:751`,
  `file_ops/file_search_byWord_util.py:368`), `import GIS_folium_map_util`
  (`gis/GIS_pipeline_util.py:551`). Convert to relative imports (CLAUDE.md).
- **[P3] Import-cycle constraint.** `Stanford_CoreNLP_util.py` imports
  `corenlp_json_*` at its bottom, so those must not import it at module level
  (shared helpers live in `corenlp_json_common.py`).
- **[P3] Single-job concurrency by design.** One `threading.Lock`; concurrent
  requests get 503. Multi-user deployment would need a real job queue.
- **[P3] Service-URL config drift.** In `core/app_constants.py`, `CORENLP_URL`
  uses the `corenlp` hostname + env override, but `MALLET_URL` is a raw
  `172.16.0.13` IP with no override; `ui/app/views.py:14` likewise defaults
  `AGENT_SERVER_URL` to a hardcoded `172.16.0.11`. Give MALLET and the agent the
  same hostname + env treatment (CLAUDE.md: never hardcode `172.16.0.x`).

## Code quality

- **[P3] ruff `PL` (pylint-port) findings suppressed as a baseline.** `pyproject.toml`
  enables ruff's `PL` family but ignores every code currently firing on legacy code:
  design metrics (`PLR09xx`, `PLR2004`), intentional patterns (`PLC0415` lazy imports,
  `PLW0603` globals), a few real low-count smells (`PLW0127` self-assign, `PLW0406`
  import-self, `PLW1510` subprocess-without-`check`, `PLW0128`), and ~113 auto-fixable
  simplifications (`PLR5501` ×79, `PLR1736` ×25, …). Clear the auto-fixable group with
  `ruff check --fix`, then drop those ignores so the rules gate new code; fix or
  knowingly keep the `PLW` smells. (Pylint proper was evaluated and declined: ~90%
  overlap with ruff+pyright, far slower, and its unique design/duplicate-code checks are
  exactly the noise this code already suppresses — ruff `PL` covers the useful slice at
  ruff speed, already in CI.)
- **[P3] ~129 inline TODO/FIXME** in `agent/src` (`grep -rn TODO agent/src`),
  mostly genuine limitations. Densest: `gis/GIS_geocode_util.py`,
  `nlp/corenlp_json_syntax.py`, `charts/`.
- **[P3] Python 3.9 ceiling.** Agent image (ubuntu:20.04) runs 3.9, so 3.10+
  syntax breaks at runtime. ruff `target-version = "py39"` guards lint but not
  hand-written code; host tests won't catch it. Revisit with a newer base image.
- **[P2] ~16 error-swallowing `except Exception: pass`/`continue`** in `agent/src`
  hide real failures — e.g. `core/reminders_util.py:471`,
  `analysis/statistics_csv_util.py:190`, `charts/charts_Plotly_util.py:98`,
  `io/IO_files_util.py:319`, `stories/shape_of_stories_vectorizer_util.py`. Narrow
  the except clause or log at warning so failures are diagnosable.
- **[P3] Dead branch in `gis/GIS_pipeline_util.py:54`** — `answer = print(...)`
  then `if answer:`; `print` returns `None` so the branch never runs (it also
  points at the removed Tips File). Drop it or restore a real prompt.

## Duplication

- **[P3] `safe_read_csv` barely adopted.** ~120 raw `.read_csv(...)` calls in
  `agent/src` vs only 4 using the `core/util.safe_read_csv` wrapper that
  standardizes encoding / `on_bad_lines` / missing-file handling. Adopt
  incrementally (boy-scout cleanup).
- **[P3] `date_get_tense` / `date_get_info` duplicated verbatim** in
  `nlp/corenlp_json_ner.py` (:34, :170) and
  `nlp/Stanford_CoreNLP_SVO_enhanced_dependencies_util.py` (:679, :655). Extract
  one shared helper.
- **[P3] `create_output_directory` reimplemented** with divergent signatures in
  `nlp/Stanford_CoreNLP_util.py:58`, `nlp/Stanza_util.py:796`,
  `nlp/spaCy_util.py:650`.
- **[P3] `WSI_classes.py` `get_batches` near-duplicate** (~40 lines) across the
  Clusterer/Matcher classes (`:30`, `:202`), differing only by a `test` parameter.

## Performance

- **[P3] Residual eager model loads** (model-load caching fixed via
  `core/model_cache.py`): `Stanza_functions_util.py` builds `stanzaPipeLine` at
  import time even for jobs that never use it (could go lazy via the cache);
  `file_spell_checker_util.py`'s `MultilingualPipeline()` calls.
- **[P3] Pervasive `df.iterrows()`/row-append loops** (~31 sites) from research
  code. Vectorize per-algorithm, only where slow.

## Security / deployment (defer until any hosted deployment)

- **[P3] Django `SECRET_KEY` hardcoded** in `ui/config/settings.py`
  (`django-insecure-`), `DEBUG` defaults on. Env-inject before any hosted deploy.
- **[P3] CORS wide open** (`allow_origins=["*"]`) on the agent. Same caveat.

## Testing

- **[P3] ~10 of 24 endpoints untested.** Remaining: file_manager, style_analysis,
  sunburst, colormap, sankey, file_search, sentence_analysis, settings (all
  small). Run tests in the agent container: `docker run --rm -v "$PWD/agent:/work"
-w /work nlp-suite-agent python3.9 -m pytest tests/`. CoreNLP-gated: add
  `--network nlp-suite_nlp-suite-network -e CORENLP_URL=http://corenlp:9000 -m
integration`; Nominatim GIS tests need `NLP_SUITE_TEST_NETWORK=1`; /word2vec +
  BERTopic/roBERTa tests need `NLP_SUITE_TEST_BERT=1` (model downloads).
- **[P3] MALLET no hermetic test.** The mallet service reads the live
  `~/nlp-suite/input`, so a test would touch real user data.
- **[P3] Assertion-light tests.** Several only check that `run_*` returns or is
  truthy — guarding against import/crash regressions but not output correctness:
  `test_boxplot.py`, `test_ner.py`, `test_excel_plotly_charts.py`,
  `test_wordnet.py`, `test_gender_analysis.py`, `test_shape_of_stories.py`, plus
  weak asserts in `test_word2vec.py`, `test_topic_modeling.py`, `test_parse.py`.
- **[P3] Duplicated test fixtures.** `_no_spacy_download` monkeypatch is copied in
  `test_parse.py:14` and `test_svo.py:12`; `_write_conll_fixture`
  (`test_wordcloud.py:87`) duplicates conftest `fixture_conll`. Move to
  `conftest.py`.
- **[P3] Fragile assertion** at `test_parse.py:139` checks exact column order
  (`assert header == [...]`); breaks on a harmless CSV reorder. Assert column
  presence instead.
- **[P3] No dependency vulnerability scan run.** `pip-audit` isn't installed and
  the pinned sets (`agent/requirements.txt`, `ui/requirements.txt`) have never
  been CVE-scanned. After `pip install pip-audit`, run
  `pip-audit -r agent/requirements.txt -r ui/requirements.txt` (or inside the
  agent image — the authoritative env; a host conda env audits the wrong deps).

## Forks (corenlp/, mallet/) — no code changes by policy

- `mallet/Dockerfile` installs unversioned `python3` + `fastapi`/`uvicorn`;
  `api.py` is live (`POST /run` on 5050 — do not delete).
- Heavy ML pins in `agent/requirements.txt` (torch 2.2.2, transformers 4.39.2,
  spacy 3.7.4) frozen; upgrading needs model-compatibility testing.
