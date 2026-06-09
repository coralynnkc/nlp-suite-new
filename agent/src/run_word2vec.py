import os
import unittest

from word2vec import run_word2vec


class TestWord2Vec(unittest.TestCase):
    def setUp(self):
        self.inputDir = "/Users/aidenamaya/nlp-suite/input"
        self.outputDir = "/Users/aidenamaya/nlp-suite/output"
        os.makedirs(self.inputDir, exist_ok=True)
        os.makedirs(self.outputDir, exist_ok=True)

        # TODO: need inputFilename?
        self.inputFilename = ""  # "Conrad_Lord Jim_01.txt"

    def test_run_word2vec_basic(self):
        # Test with minimal settings
        run_word2vec(
            inputFilename=self.inputFilename,
            inputDir=self.inputDir,
            outputDir=self.outputDir,
            chartPackage="Excel",
            dataTransformation="No transformation",
            remove_stopwords_var=False,
            lemmatize_var=False,
            WSI_var=True,
            BERT_var=False,
            Gensim_var=True,
            sg_menu_var="Skip-Gram",
            vector_size_var=100,
            window_var=5,
            min_count_var=5,
            vis_menu_var="Do not plot",
            dim_menu_var="2D",
            compute_distances_var=False,
            top_words_var=50,
            keywords_var="pigs, three",
            keywordInput="pigs",
            range4=2,
            range6=3,
            range20=5,
            ngramsDropDown="1-gram",
        )

        # for file in filesToOpen:

    # def tearDown(self):
    #     if os.path.exists(os.path.join(self.inputDir, self.inputFilename)):
    #     if os.path.exists(self.inputDir):
    #     if os.path.exists(self.outputDir):
    #         for root, dirs, files in os.walk(self.outputDir, topdown=False):
    #             for name in files:
    #             for name in dirs:


if __name__ == "__main__":
    unittest.main()
