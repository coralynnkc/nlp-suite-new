from knowledge_graphs_WordNet_main import run_kg_wordnet


def test_wordnet_noun_extraction(fixture_txt, tmp_output):
    run_kg_wordnet(
        inputFilename=str(fixture_txt),
        inputDir=str(fixture_txt.parent),
        outputDir=str(tmp_output),
        openOutputFiles=False,
        chartPackage="Matplotlib",
        dataTransformation="No transformation",
        csv_file="",
        aggregate_POS_var=False,
        noun_verb="NOUN",
        disaggregate_var=False,
        wordNet_keyword_list=[],
        annotate_file_var=False,
        extract_proper_nouns=False,
        extract_improper_nouns=False,
        aggregate_lemmatized_var=False,
        extract_nouns_verbs_from_CoNLL_var=False,
        aggregate_bySentenceID_var=False,
        dict_WordNet_filename_var="",
        hidden_noun_lemma_csv="",
        hidden_verb_lemma_csv="",
        noun_verb_menu_var="",
    )
