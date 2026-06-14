"""Sentiment analysis and word embeddings with HuggingFace transformer models.

Ported June 2026 from the upstream desktop repo's BERT_util.py. Sentiment was
ported first; word_embeddings_BERT was added when the /word2vec BERT backend was
restored (it only needs sentence-transformers + stanza + sklearn, all already in
the agent image). The upstream NER_tags_BERT and doc_summary_BERT functions
depend on packages not installed in the agent image (contextualSpellCheck,
bert-extractive-summarizer) and were not ported.

Models (downloaded from HuggingFace on first use, then cached):
  cardiffnlp/twitter-roberta-base-sentiment-latest  English sentiment
  cardiffnlp/twitter-xlm-roberta-base-sentiment     multilingual sentiment
  sentence-transformers/all-distilroberta-v1        word embeddings
"""

import csv
import logging
import os
import re
import time

import pandas as pd

from ..charts import charts_util
from ..core.model_cache import get_hf_pipeline, get_sentence_transformer
from ..io import IO_csv_util, IO_files_util, IO_internet_util

logger = logging.getLogger(__name__)

# sentence-splitting regex helpers (used by split_into_sentences)
alphabets = "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = r"(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"
digits = "([0-9])"


def sentiment_analysis_BERT(sentiment_task, inputFilename, writer, Document_ID, Document):
    """Score each sentence of inputFilename with the given HF pipeline and write rows to the csv writer."""
    with open(inputFilename, encoding="utf-8", errors="ignore") as myfile:
        fulltext = myfile.read()
    if len(fulltext) < 1:
        logger.warning("Empty file %s", inputFilename)
        return

    from .Stanza_functions_util import sentence_split_stanza_text, stanzaPipeLine

    sentences = sentence_split_stanza_text(stanzaPipeLine(fulltext))

    for i, s in enumerate(sentences, start=1):
        sentiment = sentiment_task(s)
        writer.writerow(
            {
                "Sentiment score": sentiment[0].get("score"),
                "Sentiment label": sentiment[0].get("label"),
                "Sentence ID": i,
                "Sentence": s,
                "Document ID": Document_ID,
                "Document": IO_csv_util.dressFilenameForCSVHyperlink(Document),
            }
        )


def sentiment_main(
    inputFilename,
    inputDir,
    outputDir,
    configFileName,
    mode,
    chartPackage="Excel",
    dataTransformation="No transformation",
    model_path="cardiffnlp/twitter-xlm-roberta-base-sentiment",
):
    """Run roBERTa sentiment over a single txt file or a directory of txt files."""
    # the model outputs one score and label per sentence; mode (mean/median) does not apply
    if not IO_internet_util.check_internet_availability_warning("BERT_util.py (Function sentiment_analysis_BERT)"):
        return

    filesToOpen = []

    if inputFilename == "" and inputDir == "":
        logger.warning("No input specified. Please, provide either a single txt file or a directory of txt files.")
        return

    outputDir = IO_files_util.make_output_subdirectory(
        inputFilename, inputDir, outputDir, label="sentiment_BERT", silent=True
    )
    if outputDir == "":
        return

    outputFilename = IO_files_util.generate_output_file_name(
        inputFilename, inputDir, outputDir, ".csv", "roBERTa", "", "", "", "", False, True
    )

    sentiment_task = get_hf_pipeline("sentiment-analysis", model_path, truncation=True)

    with open(outputFilename, "w", encoding="utf-8", errors="ignore", newline="") as csvfile:
        fieldnames = ["Sentiment score", "Sentiment label", "Sentence ID", "Sentence", "Document ID", "Document"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        if inputFilename != "":  # handle single file
            if not os.path.exists(inputFilename):
                logger.warning('Input file "%s" is invalid.', inputFilename)
                return
            sentiment_analysis_BERT(sentiment_task, inputFilename, writer, 1, inputFilename)
        else:  # handle directory
            if not os.path.isdir(inputDir):
                logger.warning('Input directory "%s" is invalid.', inputDir)
                return
            inputDocs = IO_files_util.getFileList(
                inputFilename, inputDir, fileType=".txt", silent=False, configFileName=configFileName
            )
            nDocs = len(inputDocs)
            documentID = 0
            for file in inputDocs:
                documentID += 1
                logger.info("Processing file %d/%d %s", documentID, nDocs, os.path.basename(file))
                filename = os.path.join(inputDir, os.fsdecode(file))
                if filename.endswith(".txt"):
                    sentiment_analysis_BERT(sentiment_task, filename, writer, documentID, filename)
    filesToOpen.append(outputFilename)

    if chartPackage != "No charts":
        outputFiles = charts_util.visualize_chart(
            chartPackage,
            dataTransformation,
            outputFilename,
            outputDir,
            columns_to_be_plotted_xAxis=[],
            columns_to_be_plotted_yAxis=["Sentiment score"],
            chart_title="Frequency of roBERTa Sentiment Scores",
            count_var=0,
            hover_label=[],
            outputFileNameType="roBERTa_scores",
            column_xAxis_label="Sentiment score",
            column_yAxis_label="Scores",
            groupByList=["Document"],
            plotList=["Sentiment Score"],
            chart_title_label="roBERTa Sentiment Scores",
        )
        if outputFiles is not None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

        outputFiles = charts_util.visualize_chart(
            chartPackage,
            dataTransformation,
            outputFilename,
            outputDir,
            columns_to_be_plotted_xAxis=[],
            columns_to_be_plotted_yAxis=["Sentiment label"],
            chart_title="Frequency of roBERTa Sentiment Labels",
            count_var=1,
            hover_label=[],
            outputFileNameType="roBERTa_labels",
            column_xAxis_label="Sentiment label",
            column_yAxis_label="Frequency",
            groupByList=["Document"],
            plotList=["Sentiment label"],
            chart_title_label="roBERTa Sentiment Labels",
        )
        if outputFiles is not None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    return filesToOpen


def split_into_sentences(text):
    text = " " + text + "  "
    text = text.replace("\n", " ")
    text = re.sub(prefixes, "\\1<prd>", text)
    text = re.sub(websites, "<prd>\\1", text)
    text = re.sub(digits + "[.]" + digits, "\\1<prd>\\2", text)
    if "..." in text:
        text = text.replace("...", "<prd><prd><prd>")
    if "Ph.D" in text:
        text = text.replace("Ph.D.", "Ph<prd>D<prd>")
    text = re.sub(r"\s" + alphabets + "[.] ", " \\1<prd> ", text)
    text = re.sub(acronyms + " " + starters, "\\1<stop> \\2", text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]", "\\1<prd>\\2<prd>\\3<prd>", text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]", "\\1<prd>\\2<prd>", text)
    text = re.sub(" " + suffixes + "[.] " + starters, " \\1<stop> \\2", text)
    text = re.sub(" " + suffixes + "[.]", " \\1<prd>", text)
    text = re.sub(" " + alphabets + "[.]", " \\1<prd>", text)
    if "”" in text:
        text = text.replace(".”", "”.")
    if '"' in text:
        text = text.replace('."', '".')
    if "!" in text:
        text = text.replace('!"', '"!')
    if "?" in text:
        text = text.replace('?"', '"?')
    text = text.replace(".", ".<stop>")
    text = text.replace("?", "?<stop>")
    text = text.replace("!", "!<stop>")
    text = text.replace("<prd>", ".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences


def word_embeddings_BERT(
    inputFilename,
    inputDir,
    outputDir,
    openOutputFiles,
    chartPackage,
    dataTransformation,
    vis_menu_var,
    dim_menu_var,
    compute_distances_var,
    top_words_var,
    keywords_var,
    lemmatize_var,
    remove_stopwords_var,
    configFileName,
):
    """Compute SentenceTransformer (distilroberta) word embeddings over a corpus.

    Ported from the upstream desktop BERT_util.word_embeddings_BERT; the leading
    tkinter `window` argument was dropped and the heavy word2vec helpers are
    imported lazily so the sentiment path does not pay their import cost.
    """
    from sklearn.manifold import TSNE

    from ..analysis import statistics_txt_util, word2vec_distances_util, word2vec_tsne_plot_util
    from ..core.model_cache import get_stanza_pipeline
    from .Stanza_functions_util import tokenize_stanza_text

    if not IO_internet_util.check_internet_availability_warning("BERT_util.py (Function word_embeddings_BERT)"):
        return []

    filesToOpen = []

    # compute only distances if inputFile is a previously-saved vector csv
    if inputFilename.endswith("csv"):
        outputFiles = word2vec_distances_util.compute_word2vec_distances(
            inputFilename,
            inputDir,
            outputDir,
            chartPackage,
            dataTransformation,
            None,
            None,
            keywords_var,
            compute_distances_var,
            top_words_var,
        )
        filesToOpen.extend(outputFiles)
        return filesToOpen

    model = get_sentence_transformer("sentence-transformers/all-distilroberta-v1")
    inputDocs = IO_files_util.getFileList(
        inputFilename, inputDir, fileType=".txt", silent=False, configFileName=configFileName
    )
    Ndocs = str(len(inputDocs))
    header = ["Word", "Vector", "Sentence ID", "Sentence", "Document ID", "Document"]
    csv_result = []
    documentID = 0
    all_words = []
    tsne_df = None

    if lemmatize_var:
        stanzaPipeLine = get_stanza_pipeline(lang="en", processors="tokenize, lemma")
        logger.info("Tokenizing and Lemmatizing...")
    else:
        stanzaPipeLine = get_stanza_pipeline(lang="en", processors="tokenize")
        logger.info("Tokenizing...")

    for doc in inputDocs:
        head, tail = os.path.split(doc)
        documentID += 1
        logger.info("Processing file " + str(documentID) + "/" + Ndocs + " " + tail)

        with open(doc, encoding="utf-8", errors="ignore") as f:
            fullText = f.read().replace("\n", " ")

        # split into sentences so the word's context can be reported in the csv
        sentences = split_into_sentences(fullText)
        for s in sentences:
            all_words.extend(tokenize_stanza_text(stanzaPipeLine(s)))

    if remove_stopwords_var:
        words_to_embed = statistics_txt_util.excludeStopWords_list(all_words)
    else:
        words_to_embed = all_words

    logger.info(
        f"Started running BERT Word2Vec model on {len(words_to_embed)} words at {time.asctime(time.localtime(time.time()))}"
    )
    word_vectors = model.encode(words_to_embed)

    word_embeddings = {}
    for w, e in zip(words_to_embed, word_vectors):
        word_embeddings[w] = e

    logger.info(
        f"Finished running BERT Word2Vec model exporting {len(word_embeddings)} non-distinct words at {time.asctime(time.localtime(time.time()))}"
    )

    # visualization
    if "Do not plot" not in vis_menu_var:
        logger.info(
            f"Started preparing charts via t-SNE for {len(word_embeddings)} non-distinct words at {time.asctime(time.localtime(time.time()))}"
        )
        if dim_menu_var == "2D":
            tsne = TSNE(n_components=2)
            xys = tsne.fit_transform(word_vectors)
            tsne_df = pd.DataFrame({"Word": words_to_embed, "x": xys[:, 0], "y": xys[:, 1]})
            fig = word2vec_tsne_plot_util.plot_interactive_graph(tsne_df)
            fig_words = word2vec_tsne_plot_util.plot_interactive_graph_words(tsne_df)
        else:
            tsne = TSNE(n_components=3)
            xyzs = tsne.fit_transform(word_vectors)
            tsne_df = pd.DataFrame({"Word": words_to_embed, "x": xyzs[:, 0], "y": xyzs[:, 1], "z": xyzs[:, 2]})
            fig = word2vec_tsne_plot_util.plot_interactive_3D_graph(tsne_df)
            fig_words = word2vec_tsne_plot_util.plot_interactive_3D_graph_words(tsne_df)

        words_outputFilename = IO_files_util.generate_output_file_name(
            inputFilename, inputDir, outputDir, "_words.html", "Word2Vec_vector_ALL_words"
        )
        fig_words.write_html(words_outputFilename)
        filesToOpen.append(words_outputFilename)

        outputFilename = IO_files_util.generate_output_file_name(
            inputFilename, inputDir, outputDir, ".html", "Word2Vec_vector_ALL_words"
        )
        fig.write_html(outputFilename)
        filesToOpen.append(outputFilename)

    logger.info(f"Started preparing the csv vector file at {time.asctime(time.localtime(time.time()))}")

    documentID = 0
    for doc in inputDocs:
        head, tail = os.path.split(doc)
        documentID += 1

        with open(doc, encoding="utf-8", errors="ignore") as f:
            fullText = f.read().replace("\n", " ")

        sentences = split_into_sentences(fullText)
        sentenceID = 0
        for s in sentences:
            sentenceID += 1
            words = tokenize_stanza_text(stanzaPipeLine(s))
            if remove_stopwords_var:
                words = statistics_txt_util.excludeStopWords_list(words)
            for w in words:
                if w in word_embeddings:
                    csv_result.append(
                        [
                            w,
                            word_embeddings[w],
                            sentenceID,
                            s,
                            documentID,
                            IO_csv_util.dressFilenameForCSVHyperlink(doc),
                        ]
                    )

    result_df = pd.DataFrame(csv_result, columns=header)

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
            BERT=True,
        )
        if outputFiles is not None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

    logger.info("Finished running BERT word embeddings")

    return filesToOpen
