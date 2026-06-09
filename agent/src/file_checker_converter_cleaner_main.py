# written by Roberto Franzosi October 2019, edited Spring 2020
# the script checks the CONTENT of txt files with various options:
#   utf-compliance
#   spelling
# the script also converts files types (pdf-->txt; docx-->txt)

import importlib

import IO_files_util
import IO_libraries_util

# RUN section ______________________________________________________________________________________________________________________________________________________


def run(
    inputFilename,
    inputDir,
    outputDir,
    openOutputFiles,
    chartPackage,
    dataTransformation,
    check_tools,
    convert_tools,
    clean_tools,
    menu_option,
    script_to_run,
    function_to_run,
):

    config_filename = "NLP_default_IO_config.csv"
    scriptName = "file_checker_converter_cleaner_main"
    filesToOpen = []

    if (check_tools == "") and (convert_tools == "") and (clean_tools == ""):
        print("No options selected: No options have been selected. Please, select one of the available options and try again.")
        return

    if menu_option == "Document converter (rtf --> txt)":
        print("rtf --> txt converter (Mac OS): In a Mac OS, use: find . -name \\*.rtf -print0 | xargs -0 textutil -convert txt")

    if ((check_tools != "") and (clean_tools != "")) and (
        (inputDir == "") and (inputFilename == "")
    ):
        print("Input error: The selected option - " + menu_option + " - requires either a txt file or a directory in input.")
        return

    if check_tools != "" or convert_tools != "" or clean_tools != "":
        if "check_for_typo" in function_to_run:
            print("Option not available: The Levenshtein's distance option is not available from this GUI. Please, run the script from the spell_checker_main.")
            return

        pythonFile = importlib.import_module(script_to_run)
        func = getattr(pythonFile, function_to_run)
        # the func function will be executed (e.g., newspaper_titles in file_cleaner_util,
        #   if function_to_run contains "newspaper title"
        # correct values are checked in NLP_GUI
        if not IO_libraries_util.check_inputPythonJavaProgramFile(
            script_to_run + ".py"
        ):
            return
        outputFile = []

        # different functions take a different number of arguments; check above in pydict and
        #   go to the function to see which arguments it takes or...
        #   standardize the number of arguments in all functions even if not used

        # predict_encoding uses default first 20 lines
        if (
            "predict_encoding" in function_to_run
            or "check_utf8" in function_to_run
            or "convert_2_ASCII" in function_to_run
            or "empty_file" in function_to_run
            or "find_replace" in function_to_run
        ):
            func(None, inputFilename, inputDir, outputDir, config_filename)
        elif "sentence_length" in function_to_run:
            outputFile = func(
                inputFilename,
                inputDir,
                outputDir,
                config_filename,
                chartPackage,
                dataTransformation,
            )
        else:
            func(
                None,
                inputFilename,
                inputDir,
                outputDir,
                config_filename,
                openOutputFiles,
                chartPackage,
                dataTransformation,
            )

        if len(outputFile) > 0:
            filesToOpen.append(outputFile)

    if openOutputFiles:
        IO_files_util.OpenOutputFiles(
            None, openOutputFiles, filesToOpen, outputDir, scriptName
        )
