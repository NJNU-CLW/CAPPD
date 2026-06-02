# README (CAPPD Project)

## Overview

The Chinese Ancient Poetry Psycholinguistic Database (CAPPD) provides a large-scale lexical resource for Chinese characters across different historical periods. The database includes lexical statistics, contextual diversity measures, phonological annotations, and diachronic distributions of over 10,000 characters.

The repository consists of one main vocabulary file (CAPPD.csv) and a sub-database folder (Diachronic_sub-database) containing dynasty-specific statistics and embeddings.

## Repository Structure

CAPPD/
│
├── CAPPD.csv                         # Main dataset file
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
├── cappd_data_builder.py         # Builds the main CAPPD dataset
├── diachronic_data_builder.py    # Generates diachronic linguistic data
├── embedding_alignment.py        # Aligns word embeddings across dynasties
├── time_series.py                # Builds time-series data
├── config.py                     # Configuration file
├── utils.py                      # Utility functions
└── embedding_eval.py             # Evaluation of embedding performance


## Data Description

- **CAPPD.csv**: Vocabulary list with lexical attributes (pinyin, frequency, Log_frequency, CD, Log_CD, Strokes, Gloss).
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

- **cappd_data_builder.py**: Generates `CAPPD.csv`.
- **diachronic_data_builder.py**: Generates files in `Diachronic_data/`.
- **embedding_alignment.py**: Trains and aligns Word2Vec models (files in `Dynasty_embeddings/`).
- **time_series.py**: Generates time series data in `Time_series/`.
- **embedding_eval.py**: Evaluates cross-dynasty word similarity after embedding alignment.
- **figure_plot.py**: Visualizes diachronic changes of word frequency diversity, entropy, and embedding similarity.

## External Resources and Licenses

The CAPPD integrates data from several openly available sources. Each external resource is cited and used in compliance with its license:

- Werneror/Poetry corpus (MIT License).
  - Source: https://github.com/Werneror/Poetry
  - → deposited at Zenodo (DOI:  https://doi.org/10.5281/zenodo.17461105).
- Chinese strokes data: Chinese-characters-code-table (BSD 2-Clause License).
  - Source: https://github.com/yefeijiang/Chinese-characters-code-table/blob/main/全部汉字码表.TXT
  - → deposited at Zenodo (DOI: https://doi.org/10.5281/zenodo.17461514).
- Pingshuiyun (平水韵) (PSY_Rhyme, Tone): https://zh.wikisource.org/wiki/平水韵 (public domain).
- Guangyun (广韵) data (GY_Rhyme, GY_Tone, GY_ID): guangyun_new.tsv, Zenodo DOI: 10.5281/zenodo.10828130.
- Unihan database (gloss): Unicode Consortium. Unihan_Readings.txt. https://www.unicode.org/Public/UCD/latest/ucd/

## Usage

1. **Download external datasets**:
   Please download the Poetry corpus, strokes data, Pingshuiyun data, and Guangyun data from the links above, and place them in the `source/` folder.

2. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Regenerate CAPPD.csv**:
    ```bash
    python code/cappd_data_builder.py
    ```

4. **Rebuild diachronic data**:
    ```bash
    python code/diachronic_data_builder.py
    ```

5. **Rebuild time series data**:
    ```bash
    python code/time_series.py
    ```

6. **Reproduce embeddings and alignment**:
    ```bash
    python code/embedding_alignment.py
    ```

7. **Evaluate the aligned embeddings**:
    ```bash
    python code/embedding_eval.py
    ```

8. **Visualize diachronic changes of word metrics**:
    ```bash
    python code/figure_plot.py
    ```

## Citation

If you use CAPPD in your research, please cite:

Wei, T., Li, J.,Tse, C.,Meng, H.,Chen, Q. (2026). A Diachronic Psycholinguistic Norms Database of Chinese Characters in Ancient Poetry (207 BC–1911 AD). Scientific Data.

## License

The CAPPD database and scripts are released under the MIT License. External resources are redistributed only via citation; please consult their original licenses.