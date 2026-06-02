import re
import numpy as np
from scipy.linalg import svd, orthogonal_procrustes
import glob
from config import *
import pandas as pd
from gensim.models import Word2Vec
import os

from sklearn.metrics.pairwise import cosine_similarity

def train_dynasty_word2vec():
    chinese_pattern = re.compile(r'[a-zA-Z,.?()（）【】\[\]!，\'" ]+')
    dynasties = ['Tang', 'Song', 'Yuan', 'Ming', 'Qing']

    # Ensure the output directory exists
    output_dir = ROOT.parent /'Diachronic_sub-database'/'Dynasty_embeddings'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for dy in dynasties:
        print(f"Training Word2Vec model for {dy} dynasty...")
        corpus_dynasty = []  # Initialize corpus for the current dynasty

        # Load poetry files for the current dynasty
        dir_dynasty = CORPUS/'dynasty_corpus'/ fr'{dy}.csv'
        # for path in glob(dir_dynasty):
        print(f"Processing file: {dir_dynasty}")
        pd_dy = pd.read_csv(dir_dynasty)
        for idx, row in pd_dy.iterrows():
            # Combine title, author, and content

            content = str(row["内容"])
            # Remove non-Chinese characters
            content_clean = chinese_pattern.sub('', content)
            # Split into sentences and convert to lists of characters
            content_clean = re.split('。|？|！|，', content_clean)
            content_clean = [list(i) for i in content_clean if i]
            corpus_dynasty.extend(content_clean)

        # Train Word2Vec model for the current dynasty
        if corpus_dynasty:
            model = Word2Vec(sentences=corpus_dynasty, vector_size=300, window=5, min_count=5, sg=1, workers=4)
            model.train(corpus_dynasty, total_examples=model.corpus_count, epochs=10)

            # Save the model
            model_path = os.path.join(output_dir, f'{dy}_word2vec.model')
            model.save(model_path)
            print(f"Word2Vec model for {dy} dynasty saved to {model_path}")




def align_embedding_space():
    def align_embeddings(reference_matrix, target_matrix):
        """
        Align the target embedding matrix to the reference embedding matrix
        :param reference_matrix: The reference embedding matrix (number of words x dimension)
        :param target_matrix: The target embedding matrix (number of words x dimension)
        :return: The aligned target embedding matrix
        """
        R, _ = orthogonal_procrustes(target_matrix, reference_matrix)
        aligned_matrix = target_matrix @ R
        return aligned_matrix

    def align_all_embeddings(models):
        """
        Align multiple embedding matrices to the same reference space
        :param models: A list of Word2Vec models
        :return: The list of aligned embedding matrices and the common vocabulary
        """
        # Get the common vocabulary of all models
        freq_df_path = ROOT.parent /'Diachronic_sub-database' / 'Diachronic_data' / 'Diachronic_character_frequencies.csv'
        freq_df = pd.read_csv(freq_df_path)
        common_characters= freq_df['Character']
        common_vocab = set(models[0].wv.index_to_key)
        for model in models[1:]:
            common_vocab.intersection_update(model.wv.index_to_key)
        common_vocab.intersection_update(common_characters)

        common_vocab = sorted(list(common_vocab))  # Sort for consistency

        # Build the embedding matrices for the common vocabulary
        embedding_matrices = []
        for model in models:

            matrix = np.array([model.wv[word] for word in common_vocab])
            embedding_matrices.append(matrix)

        # Use the first embedding matrix as the reference
        reference_matrix = embedding_matrices[0]

        # Align all other embedding matrices to the reference space
        aligned_matrices = [reference_matrix]
        for matrix in embedding_matrices[1:]:
            aligned_matrix = align_embeddings(reference_matrix, matrix)
            aligned_matrices.append(aligned_matrix)

        return aligned_matrices, common_vocab


    dynasty = ['Tang', 'Song', 'Yuan', 'Ming', 'Qing']
    # Example: Load 6 Word2Vec models and extract the embedding matrices
    model_dir= ROOT.parent /'Diachronic_sub-database'/'Dynasty_embeddings'
    model_paths = [model_dir /f'{dy}_Word2vec.model' for dy in dynasty]
    model_paths = [str(path) for path in model_paths]
    models = [Word2Vec.load(path) for path in model_paths]

    # Align all embedding matrices
    aligned_matrices, common_vocab = align_all_embeddings(models)

    # Save the aligned word vectors for each model
    for i, dy in enumerate(dynasty):

        aligned_matrix = aligned_matrices[i]
        embedding_path=ROOT.parent /'Diachronic_sub-database'/ 'Dynasty_embeddings'/'aligned_word_vectors'
        if not os.path.exists(embedding_path):
            os.makedirs(embedding_path, exist_ok=True)
        with open(embedding_path /f'{dy}_word2vec.txt', 'w', encoding='utf-8') as f:
            f.write(f"{len(common_vocab)} {aligned_matrix.shape[1]}\n")
            for j, word in enumerate(common_vocab):
                vector = ' '.join(map(str, aligned_matrix[j]))
                f.write(f"{word} {vector}\n")

    return aligned_matrices, common_vocab, models  # Output the aligned embedding spaces


if __name__ == "__main__":
    train_dynasty_word2vec()
    align_embedding_space()