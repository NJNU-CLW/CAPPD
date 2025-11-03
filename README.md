# README (CAPLD Project)

## Overview

The Chinese Ancient Poetry Lexical Database (CAPLD) provides a large-scale lexical resource for Chinese characters across different historical periods. The database includes lexical statistics, contextual diversity measures, phonological annotations, and diachronic distributions of over 10,000 characters.

The repository consists of one main vocabulary file (CAPLD.csv) and a sub-database folder (Diachronic_sub-database) containing dynasty-specific statistics and embeddings.

## Repository Structure

CAPLD/
│
├── CAPLD.csv                         # Main dataset file
├── requirements.txt                  # List of Python dependencies
├── README.md                         # Project documentation
│
├── Diachronic_sub-database/          # Sub-database for diachronic linguistic data
│   │
│   ├── Bigram_cooccurrence_matrices/ # Bigram co-occurrence matrices by dynasty
│   │   ├── co_occurence_Tang.csv
│   │   ├── co_occurence_Song.csv
│   │   ├── co_occurence_Yuan.csv
│   │   ├── co_occurence_Ming.csv
│   │   └── co_occurence_Qing.csv
│   │
│   ├── Dynasty_embeddings/           # Word embedding models for each dynasty
│   │   ├── Tang.model
│   │   ├── Song.model
│   │   ├── Yuan.model
│   │   ├── Ming.model
│   │   ├── Qing.model
│   │   └── Subtlex.model
│   │   └── aligned_word_vectors/     # Aligned word vectors across dynasties
│   │       ├── Tang_word2vec.txt
│   │       ├── Song_word2vec.txt
│   │       ├── Yuan_word2vec.txt
│   │       ├── Ming_word2vec.txt
│   │       └── Qing_word2vec.txt
│   │
│   ├── Diachronic_data/              # Diachronic character-level linguistic data
│   │   ├── Diachronic_character_frequencies.csv
│   │   ├── Diachronic_character_contextual_diversities.csv
│   │   └── Diachronic_character_phonology.csv
│   │
│   └── Time_series/                  # Time-series data 
│       ├── Diachronic_character_frequency_diversities.csv
│       ├── Diachronic_character_entropies.csv
│       └── Diachronic_character_similarities.csv
│
└── code/                         # Source code directory
├── capld_data_builder.py         # Builds the main CAPLD dataset
├── diachronic_data_builder.py    # Generates diachronic linguistic data
├── embedding_alignment.py        # Aligns word embeddings across dynasties
├── time_series.py                # Builds time-series data
├── config.py                     # Configuration file
├── utils.py                      # Utility functions
└── embedding_eval.py             # Evaluation of embedding performance


## Data Description

- **CAPLD.csv**: Vocabulary list with lexical attributes (pinyin, frequency, Log_frequency, CD, Log_CD, Strokes, Gloss).
- **Bigram_cooccurrence_matrices**: Co-occurrence counts of characters across dynasties.
- **Dynasty_embeddings**: Pre-trained Word2Vec models trained on dynasty-specific corpora, generated and aligned using `embedding_alignment.py`.
- **Diachronic_data**:
  - **Diachronic_character_frequencies.csv**: Raw and per-million frequencies of characters by dynasty.
  - **Diachronic_character_contextual_diversities.csv**: Contextual diversity measures by dynasty.
  - **Diachronic_character_phonetics.csv**: Phonological features (pinyin, PSY_Rhyme, PSY_Tone, GY_Rhyme, GY_Tone, GY_ID).
- **Time_series**:
  - **Diachronic_character_frequency_diversities.csv**: Frequency diversity values from per-million frequencies.
  - **Diachronic_character_entropies.csv**: Left and right contextual entropy values.
  - **Diachronic_character_similarities.csv**: Cosine similarities between dynasty embeddings.

See the Data Records section of the paper for full details.

## Code Description

- **capld_data_builder.py**: Generates `CAPLD.csv`.
- **diachronic_data_builder.py**: Generates files in `Diachronic_data/`.
- **embedding_alignment.py**: Trains and aligns Word2Vec models (files in `Dynasty_embeddings/`).
- **time_series.py**: Generates time series data in `Time_series/`.
- **embedding_eval.py**: Evaluates cross-dynasty word similarity after embedding alignment.
- **figure_plot.py**: Visualizes diachronic changes of word frequency diversity, entropy, and embedding similarity.

## External Resources and Licenses

The CAPLD integrates data from several openly available sources. Each external resource is cited and used in compliance with its license:

- Werneror/Poetry corpus (MIT License).
  - Source: https://github.com/Werneror/Poetry
  - deposited at Zenodo (DOI: https://doi.org/10.5281/zenodo.17461105).
- Chinese strokes data: Chinese-characters-code-table (BSD 2-Clause License).
    - Source: https://github.com/yefeijiang/Chinese-characters-code-table/blob/main/全部汉字码表.TXT
    - deposited at Zenodo (DOI: https://doi.org/10.5281/zenodo.17461514).
- Pingshuiyun (平水韵) (PSY_Rhyme, Tone): https://zh.wikisource.org/wiki/平水韵 (public domain) (accessed: 2025-10-01).
- Guangyun (广韵) data (GY_Rhyme, GY_Tone, GY_ID): guangyun_new.tsv, Zenodo (DOI: https://doi.org/10.5281/zenodo.10828130).
- Unihan database (gloss): Unicode Consortium. Unihan_Readings.txt, https://www.unicode.org/Public/UCD/latest/ucd/ (Unicode Terms of Use) (accessed: 2025-10-11)

## Usage

1. **Download external datasets**:
Please download the following datasets and place them in the specified folders:
- Poetry corpus (https://doi.org/10.5281/zenodo.17461105) : place the csv files in `source/corpus/raw_corpus/`
- Strokes data (全部汉字码表.TXT)(https://doi.org/10.5281/zenodo.17461514):  place the file in `source/`
- Gloss data (Unihan_Readings.txt) (https://www.unicode.org/Public/UCD/latest/ucd/): 
  Download the unihan.zip file from the above link, extract it, and place the `Unihan_Readings.txt` file in the `source/` folder.
- Pingshuiyun data (https://zh.wikisource.org/wiki/平水韵): 
  Visit the above page, click the "Download" button at the top right, select "Plain Text" under "Other formats", and save the resulting file as `Pingshuiyun.txt` in the `source/` folder.
- Guangyun data (guangyun_new.tsv):(DOI: https://doi.org/10.5281/zenodo.10828130)：
  Download the ZIP file from the above DOI link and extract it. Inside the extracted folder, locate the `raw` folder and place the `guangyun_new.tsv` file in your `source/` folder.
3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Regenerate CAPLD.csv**:
    ```bash
    python code/capld_data_builder.py
    ```

5. **Rebuild diachronic data**:
    ```bash
    python code/diachronic_data_builder.py
    ```

6. **Rebuild time series data**:
    ```bash
    python code/time_series.py
    ```

7. **Reproduce embeddings and alignment**:
    ```bash
    python code/embedding_alignment.py
    ```

8. **Evaluate the aligned embeddings**:
    ```bash
    python code/embedding_eval.py
    ```

9. **Visualize diachronic changes of word metrics**:
    ```bash
    python code/figure_plot.py
    ```

## License

The CAPLD database and scripts are released under the MIT License. External resources are redistributed only via citation; please consult their original licenses.
