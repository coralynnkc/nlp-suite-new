import logging
import os
import string

import gensim
import numpy as np
import pandas as pd

from ..core.app_constants import WORD_LISTS_DIR
from ..core.model_cache import get_stanza_pipeline
from ..io import IO_csv_util, IO_files_util, IO_internet_util
from . import word2vec_distances_util

logger = logging.getLogger(__name__)

_stopwords_cache = None


def _load_stopwords():
    global _stopwords_cache
    if _stopwords_cache is not None:
        return _stopwords_cache
    stopwords_path = os.path.join(str(WORD_LISTS_DIR), "stopwords.txt")
    try:
        with open(stopwords_path, encoding="utf-8") as f:
            _stopwords_cache = set(f.read().splitlines())
    except FileNotFoundError:
        logger.warning(f"stopwords file not found at {stopwords_path}")
        _stopwords_cache = set()
    return _stopwords_cache


def run_Gensim_word2vec(
    inputFilename,
    inputDir,
    outputDir,
    configFileName,
    chartPackage,
    dataTransformation,
    remove_stopwords_var,
    lemmatize_var,
    keywords_var,
    compute_distances_var,
    top_words_var,
    sg_menu_var,
    vector_size_var,
    window_var,
    min_count_var,
    vis_menu_var,
    dim_menu_var,
):
    filesToOpen = []

    logger.info("Started running Gensim Word2Vec")

    if not IO_internet_util.check_internet_availability_warning("Word2Vec_Gensim_util.py"):
        return filesToOpen

    # compute only distances if inputFile is csv
    if inputFilename.endswith("csv"):
        word_vectors = None
        result_df = None
        outputFiles = word2vec_distances_util.compute_word2vec_distances(
            inputFilename,
            inputDir,
            outputDir,
            chartPackage,
            dataTransformation,
            word_vectors,
            result_df,
            keywords_var,
            compute_distances_var,
            top_words_var,
        )
        filesToOpen.extend(outputFiles)
        return filesToOpen

    # collect all input documents
    all_input_docs = {}
    tail_list = {}
    document = []
    dId = 0

    if len(inputFilename) > 0:
        head, tail = os.path.split(inputFilename)
        if inputFilename.endswith(".txt"):
            with open(inputFilename, encoding="utf-8", errors="ignore") as file:
                dId += 1
                text = file.read()
                logger.info("Importing single file " + tail)
                document.append(IO_csv_util.dressFilenameForCSVHyperlink(inputFilename))
                all_input_docs[dId] = text
                tail_list[dId] = tail
    else:
        inputDocs = IO_files_util.getFileList(
            inputFilename, inputDir, fileType=".txt", silent=False, configFileName=configFileName
        )
        if len(inputDocs) == 0:
            return filesToOpen

        for doc in inputDocs:
            head, tail = os.path.split(doc)
            if doc.endswith(".txt"):
                with open(os.path.join(inputDir, doc), encoding="utf-8", errors="ignore") as file:
                    dId += 1
                    text = file.read()
                    logger.info("Importing file " + str(dId) + "/" + str(len(inputDocs)) + " " + tail)
                    document.append(os.path.join(inputDir, doc))
                    all_input_docs[dId] = text
                    tail_list[dId] = tail

    nFile = len(all_input_docs)

    # initialize Stanza pipeline (cached process-wide)
    if lemmatize_var:
        stanzaPipeLine = get_stanza_pipeline(lang="en", processors="tokenize, lemma")
        logger.info("Tokenizing and Lemmatizing...")
    else:
        stanzaPipeLine = get_stanza_pipeline(lang="en", processors="tokenize")
        logger.info("Tokenizing...")

    stop_words = _load_stopwords()
    punctuations = set(string.punctuation)

    all_rows = []
    sentences_out = []

    for doc_idx, (doc_id, txt) in enumerate(all_input_docs.items()):
        logger.info("Processing file " + str(doc_idx + 1) + "/" + str(nFile) + " " + tail_list[doc_id])
        stanza_doc = stanzaPipeLine(txt)

        doc_hyperlink = IO_csv_util.dressFilenameForCSVHyperlink(document[doc_idx])

        for sent_idx, sent in enumerate(stanza_doc.sentences):
            sent_text = sent.text
            temp_sent_words = []
            for word in sent.words:
                if remove_stopwords_var:
                    if word.text.lower() in stop_words or word.text in punctuations or len(word.text) == 1:
                        continue

                token_word = word.lemma if (lemmatize_var and hasattr(word, "lemma") and word.lemma) else word.text
                temp_sent_words.append(token_word)

                row = {
                    "ID": word.id,
                    "Word": word.text,
                    "Sentence ID": sent_idx + 1,
                    "Sentence": sent_text,
                    "Document ID": doc_idx + 1,
                    "Document": doc_hyperlink,
                }
                if lemmatize_var and hasattr(word, "lemma") and word.lemma:
                    row["Lemma"] = word.lemma

                all_rows.append(row)

            if temp_sent_words:
                sentences_out.append(temp_sent_words)

    out_df = pd.DataFrame(all_rows)

    sg_var = 0 if sg_menu_var == "CBOW" else 1

    logger.info("Learning architecture: " + str(sg_menu_var))

    # train model
    logger.info("Training Word2Vec model...")
    model = gensim.models.Word2Vec(
        sentences=sentences_out, sg=sg_var, vector_size=vector_size_var, window=window_var, min_count=min_count_var
    )

    word_vectors = model.wv
    words = word_vectors.key_to_index
    word_vector_list = []
    filtered_words = {}

    for v in words:
        if isinstance(v, str):
            word_vector_list.append(word_vectors[v])
            filtered_words[v] = words[v]

    if "Do not plot" not in vis_menu_var:
        from . import word2vec_tsne_plot_util

        outputFiles = word2vec_tsne_plot_util.run_word2vec_plot(
            inputFilename, inputDir, outputDir, np.asarray(word_vector_list), filtered_words, vis_menu_var, dim_menu_var
        )
        filesToOpen.extend(outputFiles)

    # build vector csv
    vector_rows = [{"key": v, "Vector": word_vectors[v]} for v in words if isinstance(v, str)]
    word_vector_df = pd.DataFrame(vector_rows)

    if lemmatize_var:
        word_vector_df.columns = ["Lemma", "Vector"]
        result_df = pd.merge(word_vector_df, out_df, on="Lemma", how="inner")
        result_df = result_df[["Word", "Lemma", "Vector", "Sentence ID", "Sentence", "Document ID", "Document"]]
    else:
        word_vector_df.columns = ["Word", "Vector"]
        result_df = pd.merge(word_vector_df, out_df, on="Word", how="inner")
        result_df = result_df[["Word", "Vector", "Sentence ID", "Sentence", "Document ID", "Document"]]

    outputFilename = IO_files_util.generate_output_file_name(
        inputFilename, inputDir, outputDir, ".csv", "Word2Vec_vector_ALL_words"
    )
    result_df.to_csv(outputFilename, encoding="utf-8", index=False)
    filesToOpen.append(outputFilename)

    if compute_distances_var:
        outputFiles = word2vec_distances_util.compute_word2vec_distances(
            inputFilename,
            inputDir,
            outputDir,
            chartPackage,
            dataTransformation,
            word_vectors,
            result_df,
            keywords_var,
            compute_distances_var,
            top_words_var,
        )
        filesToOpen.extend(outputFiles)

    logger.info("Finished running Gensim Word2Vec")

    return filesToOpen
