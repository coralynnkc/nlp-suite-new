# BERT is available as a multilingual model in 102 languages
import argparse
import csv
import os
import re
import sys
import time

import charts_util

# Visualization
import IO_csv_util
import IO_files_util
import IO_internet_util
import IO_user_interface_util
import pandas as pd
import stanza
import statistics_txt_util
import word2vec_distances_util
import word2vec_tsne_plot_util
from sentence_transformers import SentenceTransformer
from sklearn.manifold import TSNE
from summarizer import Summarizer
from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline


# Provides NER tags per sentence for every doc and stores in a csv file
def NER_tags_BERT(
    inputFilename,
    inputDir,
    outputDir,
    configFileName,
    mode,
    chartPackage,
    dataTransformation,
):
    tokenizer = AutoTokenizer.from_pretrained(
        "xlm-roberta-large-finetuned-conll03-english"
    )
    model = AutoModelForTokenClassification.from_pretrained(
        "xlm-roberta-large-finetuned-conll03-english"
    )

    inputDocs = IO_files_util.getFileList(
        inputFilename,
        inputDir,
        fileType=".txt",
        silent=False,
        configFileName=configFileName,
    )

    Ndocs = str(len(inputDocs))

    result = []
    filesToOpen = []

    if not IO_internet_util.check_internet_availability_warning(
        "BERT_util.py (Function BERT NER)"
    ):
        return

    startTime = IO_user_interface_util.timed_alert(
        2000,
        "Analysis start",
        "Started running BERT for NER annotators at",
        True,
        "",
        True,
    )

    # create output subdirectory
    outputDir = IO_files_util.make_output_subdirectory(
        inputFilename, inputDir, outputDir, label="NER_BERT", silent=True
    )

    documentID = 0
    for doc in inputDocs:
        head, tail = os.path.split(doc)
        documentID = documentID + 1
        # NER
        print("`Processing file " + str(documentID) + "/" + str(Ndocs) + " " + tail)

        header = ["Word", "NER", "Sentence ID", "Sentence", "Document ID", "Document"]
        with open(doc, encoding="utf-8", errors="ignore") as f:
            fullText = f.read()
            fullText = fullText.replace("\n", " ")

        from Stanza_functions_util import sent_tokenize_stanza, stanzaPipeLine

        sentences = sent_tokenize_stanza(stanzaPipeLine(fullText))
        sentenceID = 0

        for s in sentences:
            sentenceID = sentenceID + 1
            # this model does not use BIEOS
            # aggregation_strategy="simple" ensures that multi word entities are looked at as one entity and instead of being tagged as B-LOC and I-LOC spearately, they are just tagged as LOC together
            nlp = pipeline(
                "ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple"
            )
            ner_result = nlp(s)

            for el in ner_result:
                result.append(
                    [
                        el["word"],
                        el["entity_group"],
                        sentenceID,
                        s,
                        documentID,
                        IO_csv_util.dressFilenameForCSVHyperlink(doc),
                    ]
                )

    result.insert(0, header)

    outputFilename = IO_files_util.generate_output_file_name(
        inputFilename, inputDir, outputDir, ".csv", "NER_BERT"
    )
    IO_error = IO_csv_util.list_to_csv(result, outputFilename)

    if not IO_error:
        filesToOpen.append(outputFilename)
        import parsers_annotators_visualization_util

        kwargs = NER_dict
        outputFiles = (
            parsers_annotators_visualization_util.parsers_annotators_visualization(
                configFileName,
                inputFilename,
                inputDir,
                outputDir,
                outputFilename,
                ["NER"],
                kwargs,
                chartPackage,
                dataTransformation,
            )
        )
        if outputFiles is not None:
            if isinstance(outputFiles, str):
                filesToOpen.append(outputFiles)
            else:
                filesToOpen.extend(outputFiles)

        IO_user_interface_util.timed_alert(
            2000,
            "Analysis end",
            "Finished running BERT NER annotator at",
            True,
            "",
            True,
            startTime,
            True,
        )

        return filesToOpen


# provides summary of text per doc and stores in a csv file
def doc_summary_BERT(
    inputFilename,
    inputDir,
    outputDir,
    mode,
    chartPackage,
    dataTransformation,
    configFileName,
):

    result_summary_list = []

    header = ["Document Name", "Summary", "Document ID", "Document"]

    inputDocs = IO_files_util.getFileList(
        inputFilename,
        inputDir,
        fileType=".txt",
        silent=False,
        configFileName=configFileName,
    )

    Ndocs = str(len(inputDocs))

    documentID = 0
    for doc in inputDocs:
        head, tail = os.path.split(doc)
        documentID = documentID + 1
        # doc_summary
        print("Processing file " + str(documentID) + "/" + str(Ndocs) + " " + tail)

        with open(doc, encoding="utf-8", errors="ignore") as f:
            fullText = f.read()
            fullText = fullText.replace("\n", " ")

        bert_model = Summarizer()
        bert_summary = "".join(bert_model(fullText, min_length=60))

        result_summary_list.append(
            [
                inputFilename,
                bert_summary,
                documentID,
                IO_csv_util.dressFilenameForCSVHyperlink(doc),
            ]
        )

    result_summary_list.insert(0, header)

    tempOutputFiles = IO_files_util.generate_output_file_name(
        inputFilename, inputDir, outputDir, ".csv", "Doc_Summary_BERT"
    )
    IO_error = IO_csv_util.list_to_csv(result_summary_list, tempOutputFiles)
    if not IO_error:
        return tempOutputFiles
    return tempOutputFiles


# Creates a list of vectors/word embeddings for input files and subsequently plots them on a 2d graph
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
    model = SentenceTransformer("sentence-transformers/all-distilroberta-v1")
    inputDocs = IO_files_util.getFileList(
        inputFilename,
        inputDir,
        fileType=".txt",
        silent=False,
        configFileName=configFileName,
    )
    filesToOpen = []
    Ndocs = str(len(inputDocs))
    header = ["Word", "Vector", "Sentence ID", "Sentence", "Document ID", "Document"]
    csv_result = []
    documentID = 0
    all_words = []
    words_to_embed = []
    word_embeddings = {}
    tsne_df = None

    startTime = IO_user_interface_util.timed_alert(
        2000, "Analysis start", "Started running BERT word embeddings at", True
    )

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

    # TODO Naman notice how Word2Vec_Gensim_util has the option of using a .csv file of already computed vectors
    #   so that you can simply use this file to visualize different cosine similarities or
    #   compute distances if you had not previously done so
    # compute only distances if inputFile is csv
    # if inputFilename.endswith('csv'):
    # DONE

    # TODO Naman notice how Word2Vec_main has the option of lemmatzing
    #   this needs to be implemented similarly to Word2Vec_Gensim_util
    # DONE
    if lemmatize_var:
        stanzaPipeLine = stanza.Pipeline(lang="en", processors="tokenize, lemma")
        print("Tokenizing and Lemmatizing...")
    else:
        stanzaPipeLine = stanza.Pipeline(lang="en", processors="tokenize")
        print("Tokenizing...")

    for doc in inputDocs:
        head, tail = os.path.split(doc)
        documentID = documentID + 1
        # word embeddings
        print("Processing file " + str(documentID) + "/" + str(Ndocs) + " " + tail)

        with open(doc, encoding="utf-8", errors="ignore") as f:
            fullText = f.read()
            fullText = fullText.replace("\n", " ")

        # Splitting into sentences here so we can print out the sentence that the word is used in, in order to see the context

        sentences = split_into_sentences(fullText)
        for s in sentences:
            # add all the words from the docs into a list
            from Stanza_functions_util import stanzaPipeLine, word_tokenize_stanza

            all_words.extend(word_tokenize_stanza(stanzaPipeLine(s)))

    # remove stop words from all_words list if that option has been selected in the GUI
    if remove_stopwords_var:
        words_to_embed = statistics_txt_util.excludeStopWords_list(all_words)
    else:
        words_to_embed = all_words

    print(
        f"\nStarted running BERT Word2Vec model on {len(words_to_embed)} words at {time.asctime(time.localtime(time.time()))}"
    )
    # Creates the word embeddings per word and stores each embedding as an element in a list called embeddings
    word_vectors = model.encode(words_to_embed)

    # Creates key-value pairs of words and their corresponding vectors to be added to csv file output
    # showing words and their corresponding multidimensional vectors
    for w, e in zip(words_to_embed, word_vectors, strict=False):
        word_embeddings[w] = e

    print(
        f"\nFinished running BERT Word2Vec model exporting {len(word_embeddings)} non-distinct words at {time.asctime(time.localtime(time.time()))}"
    )

    # Plotting the word embeddings
    ## visualization
    if "Do not plot" not in vis_menu_var:
        print(
            f"\nStarted preparing charts via t-SNE for {len(word_embeddings)} non-distinct words at {time.asctime(time.localtime(time.time()))}"
        )
        if dim_menu_var == "2D":
            tsne = TSNE(n_components=2)
            xys = tsne.fit_transform(word_vectors)
            xs = xys[:, 0]
            ys = xys[:, 1]
            tsne_df = pd.DataFrame({"Word": words_to_embed, "x": xs, "y": ys})

            fig = word2vec_tsne_plot_util.plot_interactive_graph(tsne_df)
            fig_words = word2vec_tsne_plot_util.plot_interactive_graph_words(tsne_df)

        else:
            tsne = TSNE(n_components=3)
            xyzs = tsne.fit_transform(word_vectors)
            xs = xyzs[:, 0]
            ys = xyzs[:, 1]
            zs = xyzs[:, 2]
            tsne_df = pd.DataFrame({"Word": words_to_embed, "x": xs, "y": ys, "z": zs})

            fig = word2vec_tsne_plot_util.plot_interactive_3D_graph(tsne_df)
            fig_words = word2vec_tsne_plot_util.plot_interactive_3D_graph_words(tsne_df)

        print(
            f"\nSaving csv vector file and html graph output for top {top_words_var} of {len(word_embeddings)} non-distinct words at {time.asctime(time.localtime(time.time()))}"
        )

        ### write output html graph
        outputFilename = IO_files_util.generate_output_file_name(
            inputFilename, inputDir, outputDir, ".html", "Word2Vec_vector_ALL_words"
        )
        if not fig_words == "none":
            outputFilename = IO_files_util.generate_output_file_name(
                inputFilename,
                inputDir,
                outputDir,
                "_words.html",
                "Word2Vec_vector_ALL_words",
            )
            fig_words.write_html(outputFilename)
            filesToOpen.append(outputFilename)
        outputFilename = IO_files_util.generate_output_file_name(
            inputFilename, inputDir, outputDir, ".html", "Word2Vec_vector_ALL_words"
        )
        IO_files_util.generate_output_file_name(
            inputFilename,
            inputDir,
            outputDir,
            ".csv",
            "Word2Vec_top_" + str(top_words_var) + "_Euclidean_dist",
        )
        fig.write_html(outputFilename)
        filesToOpen.append(outputFilename)

    print(
        f"\nStarted preparing the csv vector file at {time.asctime(time.localtime(time.time()))}"
    )

    documentID = 0
    for doc in inputDocs:
        head, tail = os.path.split(doc)
        documentID = documentID + 1

        with open(doc, encoding="utf-8", errors="ignore") as f:
            fullText = f.read()
            fullText = fullText.replace("\n", " ")

        sentenceID = 0

        # Will add every relevant sentence s to our csv output file, so we have to loop through them here
        for s in sentences:
            sentenceID = sentenceID + 1

            # need to tokenize each sentence again here so that the words we add and check for a sentence are actually words from
            # that sentence only, and not one that comes later
            words = word_tokenize_stanza(stanzaPipeLine(s))

            if remove_stopwords_var:
                words = statistics_txt_util.excludeStopWords_list(words)

            if dim_menu_var == "2D":
                # Adding rows to our output for the csv file with words, their vectors, and the sentences they are found in
                for w in words:
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
            else:
                for w in words:
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

    print(
        f"\nSaving csv vector file for top {top_words_var} of {len(words)} non-distinct words at {time.asctime(time.localtime(time.time()))}"
    )

    result_df = pd.DataFrame(csv_result, columns=header)

    # write csv file
    outputFilename = IO_files_util.generate_output_file_name(
        inputFilename, inputDir, outputDir, ".csv", "Word2Vec_vector_ALL_words"
    )
    result_df.to_csv(outputFilename, encoding="utf-8", index=False)

    filesToOpen.append(outputFilename)

    # compute distances
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

        # # find user-selected top most-frequent words
        # # word vectors
        #
        # if not 'Do not' in vis_menu_var:
        #     # TSNE x,y (z) coordinates
        #
        #     # calculate 2-dimensional euclidean distance
        #     # TSNE x,y (z) coordinates
        #     for i, row in tmp_tsne_df.iterrows():
        #         while i < j:
        #             if 'z' not in tmp_tsne_df.columns:
        #
        # # calculate cos similarity
        # print(
        #     f'\nStarted computing cosine similarity between top {top_words_var} words at {time.asctime(time.localtime(time.time()))}')
        # for i, row in tmp_result_df.iterrows():
        #     while i < j:
        #                 [str(row['Word'])] + [str(tmp_result_df.at[j, 'Word'])])
        #             continue
        #
        # # vectors of top 10 freq words n-dimensional distance
        # for i, row in tmp_result_df.iterrows():
        #     while i < j:
        #
        # # create outputFilenames and save them
        #
        #
        #
        #
        # outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation, dist_outputFilename,
        #                                                    outputDir,
        #                                                    # count_var = 1 for columns of alphabetic values
        #                                                    count_var=0, hover_label=[],
        #                                                    chart_title_label='')
        #
        # if outputFiles!=None:
        #     if len(chart_outputFilename) > 0:
        #
        # outputFiles = charts_util.visualize_chart(chartPackage, dataTransformation, cos_sim_outputFilename,
        #                                                    outputDir,
        #                                                    # count_var = 1 for columns of alphabetic values
        #                                                    count_var=0, hover_label=[],
        #                                                    chart_title_label='')
        #
        # if outputFiles!=None:
        #     if len(chart_outputFilename) > 0:

        # len(keywords_list)) + '_Keywords_Cos_Similarity')

    IO_user_interface_util.timed_alert(
        2000,
        "Analysis end",
        "Finished running BERT word embeddings at",
        True,
        "",
        True,
        startTime,
    )

    return filesToOpen


# Performs sentiment analysis using roBERTa model
def sentiment_analysis_BERT(
    inputFilename, outputDir, outputFilename, mode, Document_ID, Document, model_path
):
    # sentiment_task = pipeline("sentiment-analysis",
    #  model=model_path, tokenizer=model_path, max_length=512, truncation=True)

    sentiment_task = pipeline(
        "sentiment-analysis", model=model_path, tokenizer=model_path, truncation=True
    )

    with open(inputFilename, encoding="utf-8", errors="ignore") as myfile:
        fulltext = myfile.read()
    # end method if file is empty
    if len(fulltext) < 1:
        print(
            "File empty",
            "The file "
            + inputFilename
            + " is empty.\n\nPlease, use another file and try again.",
        )
        print("Empty file ", inputFilename)
        return

    from Stanza_functions_util import sent_tokenize_stanza, stanzaPipeLine

    sentences = sent_tokenize_stanza(stanzaPipeLine(fulltext))

    i = 1

    for s in sentences:
        sentiment = sentiment_task(s)

        writer.writerow(
            {
                Sentiment_measure: sentiment[0].get("score"),
                Sentiment_label: sentiment[0].get("label"),
                "Sentence ID": i,
                "Sentence": s,
                "Document ID": Document_ID,
                "Document": IO_csv_util.dressFilenameForCSVHyperlink(Document),
            }
        )

        i += 1

    return outputFilename


# helper main method for sentiment analysis
def sentiment_main(
    inputFilename,
    inputDir,
    outputDir,
    configFileName,
    mode,
    chartPackage="Excel",
    dataTransformation="No Transformation",
    model_path="cardiffnlp/twitter-xlm-roberta-base-sentiment",
):
    """
    Runs analyzefile on the appropriate files, provided that the input paths are valid.
    :param inputFilename:
    :param inputDir:
    :param outputDir:
    :return:

    """

    if not IO_internet_util.check_internet_availability_warning(
        "BERT_util.py (Function sentiment_analysis_BERT)"
    ):
        return

    filesToOpen = []

    if len(outputDir) < 0 or not os.path.exists(outputDir):
        print("No output directory specified, or path does not exist.")
        sys.exit(1)
    elif len(inputFilename) == 0 and len(inputDir) == 0:
        print(
            "No input specified. Please, provide either a single file -- file or a directory of files to be analyzed --dir."
        )
        sys.exit(1)

    # create a subdirectory of the output directory
    outputDir = IO_files_util.make_output_subdirectory(
        inputFilename, inputDir, outputDir, label="sentiment_BERT", silent=True
    )
    if outputDir == "":
        return

    outputFilename = IO_files_util.generate_output_file_name(
        inputFilename,
        inputDir,
        outputDir,
        ".csv",
        "roBERTa",
        "",
        "",
        "",
        "",
        False,
        True,
    )

    # check each word in sentence for sentiment and write to output_file
    with open(
        outputFilename, "w", encoding="utf-8", errors="ignore", newline=""
    ) as csvfile:
        global Sentiment_measure, Sentiment_label
        Sentiment_measure = "Sentiment score"
        Sentiment_label = "Sentiment label"
        fieldnames = [
            Sentiment_measure,
            Sentiment_label,
            "Sentence ID",
            "Sentence",
            "Document ID",
            "Document",
        ]
        global writer
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        if len(inputFilename) > 0:  # handle single file
            if os.path.exists(inputFilename):
                filesToOpen.append(
                    sentiment_analysis_BERT(
                        inputFilename,
                        outputDir,
                        outputFilename,
                        mode,
                        1,
                        inputFilename,
                        model_path,
                    )
                )
                sentiment_analysis_BERT(
                    inputFilename,
                    outputDir,
                    outputFilename,
                    mode,
                    1,
                    inputFilename,
                    model_path,
                )
            else:
                print('Input file "' + inputFilename + '" is invalid.')
                sys.exit(1)
        elif len(inputDir) > 0:  # handle directory
            documentID = 0
            if os.path.isdir(inputDir):
                os.fsencode(inputDir)
                inputDocs = IO_files_util.getFileList(
                    inputFilename,
                    inputDir,
                    fileType=".txt",
                    silent=False,
                    configFileName=configFileName,
                )
                nDocs = len(inputDocs)
                for file in inputDocs:
                    head, tail = os.path.split(file)
                    # sentiment analysis
                    documentID = documentID + 1
                    print(
                        "Processing file "
                        + str(documentID)
                        + "/"
                        + str(nDocs)
                        + " "
                        + tail
                    )
                    filename = os.path.join(inputDir, os.fsdecode(file))
                    if filename.endswith(".txt"):
                        time.time()
                        documentID += 1
                        filesToOpen.append(
                            sentiment_analysis_BERT(
                                filename,
                                outputDir,
                                outputFilename,
                                mode,
                                documentID,
                                filename,
                                model_path,
                            )
                        )
            else:
                print('Input directory "' + inputDir + '" is invalid.')
    csvfile.close()

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
            outputFileNameType="roBERTa_scores",  # 'line_bar',
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
            outputFileNameType="roBERTa_labels",  # 'line_bar',
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


if __name__ == "__main__":
    # get arguments from command line
    parser = argparse.ArgumentParser(description="Sentiment analysis with BERT")
    parser.add_argument(
        "--file",
        type=str,
        dest="inputFilename",
        default="",
        help='a string to hold the INPUT path and filename if only ONE txt file is processed; enter --file "" or eliminate --file flag to process ALL txt files in input directory; use "" if path and filenames contain spaces',
    )
    parser.add_argument(
        "--dir",
        type=str,
        dest="inputDir",
        default="",
        help='a string to hold the INPUT path of the directory of ALL txt files to be processed; use "" if path contains spaces',
    )
    parser.add_argument(
        "--out",
        type=str,
        dest="outputDir",
        default="",
        help='a string to hold the path of the OUTPUT directory; use "" if path contains spaces',
    )
    parser.add_argument(
        "--configFileName",
        type=str,
        dest="outputDir",
        default="",
        help="a string to hold the path of the configFileName",
    )
    parser.add_argument(
        "--outfile", type=str, dest="outputFilename", default="", help="output file"
    )

    parser.add_argument(
        "--mode",
        type=str,
        dest="mode",
        default="mean",
        help="mode with which to calculate sentiment in the sentence: mean or median",
    )
    args = parser.parse_args()

# very fast method to split a text file into a list whose elements are each sentence in that file. Found on: https://stackoverflow.com/a/31505798
# -*- coding: utf-8 -*-

alphabets = "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = r"(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"
digits = "([0-9])"


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
    text = re.sub(
        alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]",
        "\\1<prd>\\2<prd>\\3<prd>",
        text,
    )
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


NER_dict = {
    "NERs": [
        "geo",  # for geographical entity
        "org",  # for organization entity
        "per",  # for person entity
        "gpe",  # for geopolitical entity
        "tim",  # for time indicator entity
        "art",  # for artifact entity
        "eve",  # for event entity
        "nat",  # for natural phenomenon entity
        "O",  # is assigned if a word doesn’t belong to any entity.
    ]
}
