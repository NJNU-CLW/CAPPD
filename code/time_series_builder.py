
import math
from collections import defaultdict
import string
from config import *
from embedding_alignment import *

def calculate_entropy(frequencies):
    # Function to calculate entropy given a dictionary of frequencies
    total = sum(frequencies.values())
    entropy = -sum((freq / total) * math.log2(freq / total) for freq in frequencies.values() if freq > 0)
    return entropy

def generate_Entropy():
    # Function to calculate left and right entropies for each character in each dynasty and combine them into CSV files
    dynasties = ['Tang', 'Song', 'Yuan', 'Ming', 'Qing']
    punctuation_and_space = string.punctuation + ' ' + '，。！？；：（）【】《》“”‘’——……'
    freq_df_path= ROOT.parent /'Diachronic_sub-database'/ 'Diachronic_data' / 'Diachronic_character_frequencies.csv'
    vocab_df = pd.read_csv(freq_df_path)
    characters = vocab_df["Character"].tolist()
    entropy_df=pd.DataFrame({'Character':characters})
    entropy_df['pinyin']=vocab_df['pinyin']
    entropy_df['Gloss']=vocab_df['Gloss']
    for dy in dynasties:
        left_neighbors = defaultdict(lambda: defaultdict(int))
        right_neighbors = defaultdict(lambda: defaultdict(int))
        dir_path =  CORPUS / 'dynasty_corpus'/ f'{dy}.csv'
        each_dy_poems = pd.read_csv(dir_path)
        for _, row in each_dy_poems.iterrows():
            text = str(row["内容"])

            for i in range(1, len(text) - 1):
                char = text[i]
                if char in characters:
                    if text[i - 1] not in punctuation_and_space:
                        left_neighbors[char][text[i - 1]] = left_neighbors[char].get(text[i - 1], 0) + 1
                    if text[i + 1] not in punctuation_and_space:
                        right_neighbors[char][text[i + 1]] = right_neighbors[char].get(text[i + 1], 0) + 1
        dy_left_entropy=[]
        dy_right_entropy=[]

        for i, char in enumerate(characters):
            left_entropy = calculate_entropy(left_neighbors[char])
            right_entropy = calculate_entropy(right_neighbors[char])
            dy_left_entropy.append(left_entropy)
            dy_right_entropy.append(right_entropy)
        entropy_df[fr'{dy}_left_entropy']=dy_left_entropy
        entropy_df[fr'{dy}_right_entropy'] = dy_right_entropy

    save_path=ROOT.parent /'Diachronic_sub-database'/ 'time_series' /'Diachronic_entropies.csv'
    entropy_df.to_csv( save_path , index=False)
    print(f"Entropy data has been saved to {save_path}")


def generate_frequency_diversity():
    # Define the list of dynasties
    dynasties = ['Tang', 'Song', 'Yuan', 'Ming', 'Qing']
    # Load the frequency data
    input_file = ROOT.parent /'Diachronic_sub-database'/ 'Diachronic_data' /'Diachronic_character_frequencies.csv'
    if not os.path.exists(input_file):
        print(f"Input file not found: {input_file}")
        return
    df = pd.read_csv(input_file)
    # Initialize columns for frequency diversity and log frequency diversity
    for dy in dynasties[1:]:  # Skip Tang dynasty as it is the reference
        df[f'{dy}_fd'] = df[f'PerMillion_{dy}'] / df['PerMillion_Tang']
        df[f'{dy}_log_fd'] = np.log10(df[f'{dy}_fd'])
    # Select and reorder the columns as specified

    output_columns = ['Character'] + [f'{dy}_fd' for dy in dynasties[1:]]+ [f'{dy}_log_fd' for dy in dynasties[1:]]
    df = df[output_columns]
    # Ensure the output directory exists
    output_dir = ROOT.parent / 'Diachronic_sub-database' /'time_series'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # Save the results to a new CSV file
    output_file = os.path.join(output_dir, 'Diachronic_character_frequency_diversities.csv')
    df.to_csv(output_file, index=False)
    print(f"Frequency diversity data has been saved to {output_file}")

def generate_dynasty_cosine_similarity():
    aligned_matrices,common_vocab,models=align_embedding_space()
    # Get the first matrix as the base matrix
    base_matrix = aligned_matrices[0]
    other_matrices = aligned_matrices[1:]

    # Initialize the result list
    results = []

    # Iterate through each word in the common vocabulary
    for idx, word in enumerate(common_vocab):
        # Get the vector of the current word in the base matrix
        base_vector = base_matrix[idx].reshape(1, -1)

        # Calculate the cosine similarity with the corresponding word vectors in other matrices
        similarities = []
        for matrix in other_matrices:
            other_vector = matrix[idx].reshape(1, -1)
            similarity = cosine_similarity(base_vector, other_vector)[0][0]
            similarities.append(similarity)

        # Append the result to the list
        results.append([word] + similarities)

    # Create a DataFrame

    columns = ['Character', 'Tang&Song', 'Tang&Yuan', 'Tang&Ming', 'Tang&Qing']
    df = pd.DataFrame(results, columns=columns)

    # Save to a CSV file

    save_path=ROOT.parent / 'Diachronic_sub-database'/'time_series'/'Diachronic_character_similarities.csv'
    df.to_csv(save_path, index=False)
    print("Cosine similarity results have been saved to 'Diachronic_character_similarities.csv'.")

if __name__=="__main__":
    # generate_Entropy()
    # generate_frequency_diversity()
    generate_dynasty_cosine_similarity()