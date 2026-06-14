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

## Code quality

- **[P3] ~129 inline TODO/FIXME** in `agent/src` (`grep -rn TODO agent/src`),
  mostly genuine limitations. Densest: `gis/GIS_geocode_util.py`,
  `nlp/corenlp_json_syntax.py`, `charts/`.
- **[P3] Python 3.9 ceiling.** Agent image (ubuntu:20.04) runs 3.9, so 3.10+
  syntax breaks at runtime. ruff `target-version = "py39"` guards lint but not
  hand-written code; host tests won't catch it. Revisit with a newer base image.

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

## Forks (corenlp/, mallet/) — no code changes by policy

- `mallet/Dockerfile` installs unversioned `python3` + `fastapi`/`uvicorn`;
  `api.py` is live (`POST /run` on 5050 — do not delete).
- Heavy ML pins in `agent/requirements.txt` (torch 2.2.2, transformers 4.39.2,
  spacy 3.7.4) frozen; upgrading needs model-compatibility testing.
