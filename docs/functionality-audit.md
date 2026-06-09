# Functionality Audit

Audit of all three repos as of initial migration. Source of truth: `NLP-Suite/src/` (177 Python files).

---

## NLP-Suite/src — categorized by tool

### Parsing & Annotation (Stanford CoreNLP, spaCy, Stanza)
| File | Task | Dependencies |
|------|------|--------------|
| `Stanford_CoreNLP_util.py` | Dependency parsing, semantic role labeling | Stanford CoreNLP, pycorenlp |
| `Stanford_CoreNLP_tags_util.py` | POS tagging, morphological analysis | Stanford CoreNLP |
| `Stanford_CoreNLP_clause_util.py` | Clause extraction | Stanford CoreNLP |
| `Stanford_CoreNLP_coreference_util.py` | Coreference resolution | Stanford CoreNLP |
| `Stanford_CoreNLP_SVO_enhanced_dependencies_util.py` | SVO extraction with enhanced deps | Stanford CoreNLP |
| `spaCy_util.py` | Multi-language pipeline (tokenize, POS, NER, dep parse) | spaCy, spacytextblob |
| `Stanza_util.py` | Neural NLP pipeline | Stanza |
| `parsers_annotators_main.py` | Parser/annotator selection entrypoint | CoreNLP, spaCy, Stanza |

### Named Entity Recognition
| File | Task | Dependencies |
|------|------|--------------|
| `NER_main.py` | NER extraction | CoreNLP, spaCy, Stanza |
| `BERT_util.py` | BERT-based NER and token classification | transformers, sentence-transformers |

### Sentiment Analysis
| File | Task | Dependencies |
|------|------|--------------|
| `sentiment_analysis_VADER_util.py` | VADER rule-based sentiment | NLTK VADER |
| `sentiment_analysis_ANEW_util.py` | ANEW lexicon sentiment | ANEW word lists |
| `sentiment_analysis_SentiWordNet_util.py` | SentiWordNet sentiment | WordNet |
| `sentiment_analysis_hedonometer_util.py` | Hedonometer happiness scores | External lexicon |
| `sentiments_emotions_ALL_main.py` | Multi-method sentiment aggregator | All above |

### Topic Modeling
| File | Task | Dependencies |
|------|------|--------------|
| `topic_modeling_gensim_util.py` | LDA and related methods | Gensim, scikit-learn |
| `topic_modeling_mallet_util.py` | MALLET LDA wrapper | MALLET (Java), subprocess |
| `topic_modeling_bert_util.py` | BERTopic zero-shot modeling | BERTopic, sentence-transformers |

### Word Embeddings
| File | Task | Dependencies |
|------|------|--------------|
| `word2vec_Gensim_util.py` | Skip-gram and CBOW | Gensim |
| `word2vec_distances_util.py` | Word similarity/distance | Gensim, numpy |
| `word2vec_tsne_plot_util.py` | t-SNE visualization | sklearn, matplotlib |
| `WSI_util.py` | Word Sense Induction | Gensim, clustering |

### Syntactic & Semantic Analysis
| File | Task | Dependencies |
|------|------|--------------|
| `SVO_main.py` | Subject-Verb-Object extraction | CoreNLP |
| `CoNLL_table_analyzer_main.py` | CoNLL linguistic table analysis | Gephi, pandas |
| `CoNLL_adjective/adverb/verb/noun/clause_analysis_util.py` | POS-specific frequency analysis | pandas |
| `coreference_main.py` | Coreference chain extraction | CoreNLP |
| `sentence_analysis_main.py` | Sentence length, complexity, readability | CoreNLP |

### Style & Readability
| File | Task | Dependencies |
|------|------|--------------|
| `style_analysis_main.py` | Complexity and vocabulary analysis | Readability indices |
| `style_analysis_abstract_concreteness_analysis_util.py` | Abstract/concrete word analysis | External lexicon |

### N-gram & Co-occurrence
| File | Task | Dependencies |
|------|------|--------------|
| `NGrams_util.py` | N-gram extraction and frequency | NLTK |
| `NGrams_CoOccurrences.py` | Co-occurrence analysis | pandas, Plotly |

### Narrative Analysis
| File | Task | Dependencies |
|------|------|--------------|
| `shape_of_stories_main.py` | Narrative arc detection | Sentiment, vectorization |
| `shape_of_stories_vectorizer_util.py` | Story vectorization | sklearn, gensim |
| `shape_of_stories_clustering_util.py` | Story shape clustering | sklearn, scipy |

### Knowledge Graphs
| File | Task | Dependencies |
|------|------|--------------|
| `knowledge_graphs_WordNet_main.py` | WordNet semantic network | NLTK WordNet |
| `knowledge_graphs_DBpedia_YAGO_main.py` | DBpedia/YAGO entity linking | SPARQL, requests |

### Geographic Analysis (GIS)
| File | Task | Dependencies |
|------|------|--------------|
| `GIS_main.py` | Location extraction and mapping | Geopy, folium |
| `GIS_Google_Maps_util.py` | Google Maps API integration | googlemaps SDK |
| `GIS_geocode_util.py` | Geocoding (text → coordinates) | Nominatim, Geopy |
| `GIS_folium_map_util.py` | Interactive map creation | folium |
| `GIS_distance_util.py` | Distance matrix computation | pandas, numpy |

### Gender Analysis
| File | Task | Dependencies |
|------|------|--------------|
| `html_annotator_gender_main.py` | Name-based gender classification | gender-guesser |

### Visualization
| File | Task | Dependencies |
|------|------|--------------|
| `charts_Plotly_util.py` | Interactive Plotly charts | Plotly, pandas |
| `charts_Excel_main.py` | Excel chart export | openpyxl |
| `charts_matplotlib_seaborn_util.py` | Statistical plots | seaborn, matplotlib |
| `wordclouds_main.py` | Word cloud generation | wordcloud, PIL |

### File Management & Preprocessing
35+ files covering: search, split, merge, clean, validate, rename, classify, deduplicate. See `NLP-Suite/src/` directly.

---

## nlp-suite-agent — existing endpoints

Framework: FastAPI. All `POST` unless noted.

| Endpoint | Purpose |
|----------|---------|
| `GET /status` | Health check |
| `POST /file_manager` | File ops (rename, copy, move, delete, split, filter) |
| `POST /sentiment_analysis` | Multi-lexicon sentiment scoring |
| `POST /topic_modeling` | LDA via Gensim, MALLET, or BERTopic |
| `POST /parsers_annotators` | POS, dependency parsing, annotation |
| `POST /word2vec` | Word embeddings with visualization |
| `POST /CoNLL_table_analyzer_main` | CoNLL linguistic table analysis |
| `POST /style_analysis` | Readability, complexity, vocabulary |
| `POST /sunburst_charts` | Hierarchical data visualization |
| `POST /colormap_chart` | Heatmap/colormap visualization |
| `POST /sankey_flowchart` | Flow diagram visualization |
| `POST /SVO` | Subject-Verb-Object extraction |
| `POST /wordclouds` | Word cloud generation |
| `POST /NGrams_CoOccurrences` | N-gram and co-occurrence analysis |
| `POST /filesearchword` | Keyword search across corpus |
| `POST /document_statistics` | Corpus-level text statistics |
| `POST /sentence_analysis` | Sentence-level analysis |
| `POST /gis` | Geographic extraction and mapping |

---

## nlp-suite-ui — pages and features

Framework: Django + HTML/JS templates.

| Template | Feature | Has agent endpoint? |
|----------|---------|-------------------|
| `file_manager.html` | File organization | ✅ |
| `sentiment_analysis.html` | Sentiment analysis | ✅ |
| `topic_modeling.html` | Topic modeling | ✅ |
| `parsers_annotators.html` | Linguistic parsing | ✅ |
| `word2vec.html` | Word embeddings | ✅ |
| `CoNLL_table_analyzer_main.html` | CoNLL analysis | ✅ |
| `style_analysis.html` | Style/readability | ✅ |
| `sunburst_charts.html` | Sunburst charts | ✅ |
| `colormap_chart.html` | Heatmap | ✅ |
| `sankey_flowchart.html` | Sankey diagram | ✅ |
| `SVO.html` | SVO extraction | ✅ |
| `wordclouds.html` | Word clouds | ✅ |
| `NGrams_CoOccurrences.html` | N-grams | ✅ |
| `filesearchword.html` | Keyword search | ✅ |
| `document_statistics.html` | Text statistics | ✅ |
| `sentence_analysis.html` | Sentence analysis | ✅ |
| `gis.html` | GIS mapping | ✅ |
| `NER.html` | Named entity recognition | ❌ needs `/ner` |
| `wordnet.html` | WordNet graphs | ❌ needs `/wordnet` |
| `gender_analysis.html` | Gender classification | ❌ needs `/gender_analysis` |
| `shape_of_stories.html` | Narrative arc | ❌ needs `/shape_of_stories` |
| `excel_plotly_charts.html` | Interactive charts | ❌ needs `/excel_plotly_charts` |
| `boxplot.html` | Statistical boxplots | ❌ needs `/boxplot` |
