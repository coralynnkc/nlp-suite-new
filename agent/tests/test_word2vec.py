"""Tests for /word2vec.

The three backends (Gensim, WSI, BERT word embeddings) were ported from the
desktop repo in June 2026; see TECH_DEBT.md. The guard tests below need no heavy
deps and run wherever word2vec imports; the backend tests download models
(stanza English for Gensim, bert-base-uncased for WSI, distilroberta for BERT) on
first run and are gated behind NLP_SUITE_TEST_BERT. Run them in the agent image:
    docker run --rm -e NLP_SUITE_TEST_BERT=1 -v "$PWD/agent:/work" -w /work \
        nlp-suite-agent python3.9 -m pytest tests/test_word2vec.py -v
"""

import os
import pathlib

import pytest
from conftest import output_csvs

try:
    from word2vec import run_word2vec
except (ImportError, SystemExit):
    pytest.skip("word2vec dependencies not available", allow_module_level=True)


requires_models = pytest.mark.skipif(
    not os.environ.get("NLP_SUITE_TEST_BERT"),
    reason="downloads HuggingFace/stanza models; set NLP_SUITE_TEST_BERT=1 to run",
)


def _run(inputDir, tmp_output, **kwargs):
    args = dict(
        inputFilename="",
        inputDir=str(inputDir),
        outputDir=str(tmp_output),
        chartPackage="No charts",
        dataTransformation="No transformation",
        remove_stopwords_var=False,
        lemmatize_var=False,
        WSI_var=False,
        BERT_var=False,
        Gensim_var=False,
        sg_menu_var="Skip-Gram",
        vector_size_var=100,
        window_var=5,
        min_count_var=5,
        vis_menu_var="Do not plot",
        dim_menu_var="2D",
        compute_distances_var=False,
        top_words_var=200,
        keywords_var="",
        keywordInput="",
        range4=4,
        range6=6,
        range20=10,
        ngramsDropDown="3-grams (unigrams)",
    )
    args.update(kwargs)
    return run_word2vec(**args)


def _output_files(outputDir, suffix):
    return sorted(str(p) for p in pathlib.Path(outputDir).rglob(f"*{suffix}"))


# --- guard paths (no heavy deps) -------------------------------------------


def test_no_options_selected_returns_none(tiny_corpus, tmp_output):
    assert _run(tiny_corpus, tmp_output) is None
    assert output_csvs(tmp_output) == []


def test_compute_distances_alone_is_a_noop(tiny_corpus, tmp_output):
    # passes the no-option guard but no backend is selected: returns an
    # empty file list and writes nothing
    assert _run(tiny_corpus, tmp_output, compute_distances_var=True) == []
    assert output_csvs(tmp_output) == []


def test_wsi_without_keywords_returns_none(tiny_corpus, tmp_output):
    # the keyword guard fires before any WSI work (an empty WSI subdirectory
    # is still created)
    assert _run(tiny_corpus, tmp_output, WSI_var=True, keywordInput="") is None
    assert output_csvs(tmp_output) == []


# --- backend paths (gated: model downloads) --------------------------------


@requires_models
def test_gensim_backend_runs(tiny_corpus, tmp_output):
    # min_count=1 so the small corpus actually yields a vocabulary
    result = _run(tiny_corpus, tmp_output, Gensim_var=True, min_count_var=1)
    assert result  # non-empty list of produced files
    vector_csvs = [f for f in output_csvs(tmp_output) if "Word2Vec_vector_ALL_words" in f]
    assert len(vector_csvs) == 1


@requires_models
def test_bert_backend_runs(tiny_corpus, tmp_output):
    result = _run(tiny_corpus, tmp_output, BERT_var=True)
    assert result
    vector_csvs = [f for f in output_csvs(tmp_output) if "Word2Vec_vector_ALL_words" in f]
    assert len(vector_csvs) == 1


@requires_models
def test_wsi_backend_runs(wsi_corpus, tmp_output):
    # 'spring' recurs 12 times across senses; k-range (2,4) clusters cleanly
    result = _run(
        wsi_corpus,
        tmp_output,
        WSI_var=True,
        keywordInput="spring",
        range4=2,
        range6=4,
        range20=5,
    )
    assert result  # cluster-sentence txts + sense-bar pngs + key-term csv
    assert any("clusters" in f for f in result)
    assert any(f.endswith(".png") for f in result)
    assert _output_files(tmp_output, ".csv")  # key-terms csv written
