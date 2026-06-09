import pytest

# html_annotator_gender_main imports GUI_util (tkinter) at module level;
# skip the whole module if it can't be imported.
html_annotator_gender_main = pytest.importorskip("html_annotator_gender_main")
run_gender_analysis = html_annotator_gender_main.run


@pytest.mark.integration
def test_gender_analysis_corenlp(fixture_txt, tmp_output, corenlp_running):
    run_gender_analysis(
        inputFilename=str(fixture_txt),
        input_main_dir_path=str(fixture_txt.parent),
        outputDir=str(tmp_output),
        openOutputFiles=False,
        chartPackage="Matplotlib",
        dataTransformation="No transformation",
        CoreNLP_gender_annotator_var=True,
        CoreNLP_download_gender_file_var=False,
        CoreNLP_upload_gender_file_var=False,
        annotator_dictionary_var=False,
        annotator_dictionary_file_var="",
        personal_pronouns_var=False,
        plot_var=False,
        year_state_var="",
        firstName_entry_var="",
        new_SS_folders=[],
    )
