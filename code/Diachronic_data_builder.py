# -*- coding:utf-8 -*-
import csv
from collections import Counter
import numpy as np
from gensim.models import Word2Vec
from utils import *
from opencc import OpenCC
import string
import re

cedict = load_char_def()



def generate_dynasty_char_vocab():
    # generate char_vocabulary for each dynasty
    chinese_pattern = re.compile(r'[^\u4e00-\u9fa5]')

    dynasty = 'Tang Song Yuan Ming Qing'.split()
    path = SOURCE/'corpus'/'dynasty_corpus'
    for dy in dynasty:
        dy_path=path / f'{dy}.csv'
        corpus_dynasty = ""

        pd_dy = pd.read_csv(dy_path)
        for idx,row in pd_dy.iterrows():

            content = str(row['内容'])
            content_clean = chinese_pattern.sub('', content)
            corpus_dynasty += content_clean

        char_counter = Counter(corpus_dynasty)

        char_vocab_sorted = char_counter.most_common()


        csv_file =OUTPUT / f'Char_vocab_{dy}.csv'
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Character', 'Frequency'])
            csv_writer.writerows(char_vocab_sorted)

        print(f"Sorted character vocabulary saved to {csv_file}")




def generate_diachronic_characters_frequency():
    # Define the list of dynasties
    dynasties = ['Tang', 'Song', 'Yuan', 'Ming', 'Qing']
    # Initialize a dictionary to store the vocabulary data for each dynasty
    dynasty_data = {}

    dy_total={}
    for dy in dynasties:
        file_path =OUTPUT / f'char_vocab_{dy}.csv'  # Assume the file path
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            # Convert the data to a dictionary with Character as key and Frequency as value
            dynasty_data[dy] = df.set_index('Character')['Frequency'].to_dict()
            dy_total[dy]=df['Frequency'].sum()
        else:
            print(f"File not found: {file_path}")
            return

    # Find characters that are common across all dynasties
    common_characters = set(dynasty_data[dynasties[0]].keys())
    for dy in dynasties[1:]:
        common_characters = common_characters.intersection(set(dynasty_data[dy].keys()))
    # common_characters =common_characters.intersection(subtlex.keys())
    result_data = []
    for char in common_characters:
        raw_frequencies = [dynasty_data[dy].get(char, 0) for dy in dynasties]
        per_million_frequencies = [
            freq / dy_total[dy] * 1_000_000 if dy_total[dy] else 0 for freq, dy in zip(raw_frequencies, dynasties)
        ]
        # raw_sub = subtlex[char]['Frequency']
        # pmillion_sub =  subtlex[char]['Frequency_million']
        pinyin = get_pinyin(char)
        gloss=cedict.get(char, '-')
        result_data.append([pinyin,*raw_frequencies,*per_million_frequencies,gloss])

    # Create a DataFrame from the result list
    columns = ['pinyin','Raw_Tang', 'Raw_Song', 'Raw_Yuan', 'Raw_Ming', 'Raw_Qing',
               'PerMillion_Tang', 'PerMillion_Song', 'PerMillion_Yuan', 'PerMillion_Ming', 'PerMillion_Qing','Gloss']
    result_df = pd.DataFrame(result_data, index=list(common_characters), columns=columns)
    result_df = result_df.sort_values(by='Raw_Tang', ascending=False)
    output_file = ROOT.parent/'Diachronic_sub-database' /'Diachronic_data'/'Diachronic_character_frequencies.csv'
    result_df.to_csv(output_file, index_label='Character')
    return result_df


def generate_diachronic_diversity():
    # Define the list of dynasties
    dynasties = ['Tang', 'Song', 'Yuan', 'Ming', 'Qing']
    DYNASTY_TOTALS = {
        'Tang': 50313,
        'Song': 305188,
        'Yuan': 53111,
        'Ming': 254657,
        'Qing': 117924
    }
    freq_df=generate_diachronic_characters_frequency()
    common_characters=freq_df.index.tolist()
    pinyin=freq_df['pinyin']
    gloss=freq_df['Gloss']

    dynasty_diversity = {}
    for dy in dynasties:
        file_path = CORPUS / 'dynasty_corpus' / f'{dy}.csv'
        column_name = f'{dy}_diversity'
        normalized_cd=f'{dy}_CD%'
        if not os.path.exists(file_path):
            print(f'跳过：{file_path} 不存在')
            dynasty_diversity[column_name] = pd.Series(0, index=common_characters, name=column_name)
            continue

        dynasty_diversity[column_name]={c:0 for c in common_characters}
        dynasty_diversity[normalized_cd] = {c: 0 for c in common_characters}
        poems_df = pd.read_csv(file_path)
        for _, row in poems_df.iterrows():
            text = str(row['内容'])
            for char in common_characters:
                if char in text:
                    dynasty_diversity[column_name][char] += 1
                dynasty_diversity[normalized_cd][char]=dynasty_diversity[column_name][char]/DYNASTY_TOTALS[dy]


    dynasty_df = pd.DataFrame(dynasty_diversity)
    result_df = pd.DataFrame({'Character':common_characters,'pinyin':pinyin,'gloss':gloss})
    result_df=result_df.merge(dynasty_df, left_on='Character', right_index=True, how='left')

    columns_order = ['Character', 'pinyin'] + [f'{dy}_diversity' for dy in dynasties] + [f'{dy}_CD%' for dy in dynasties]+['gloss']
    result_df = result_df[columns_order]
    result_df = pd.DataFrame(result_df)
    output_file = ROOT.parent / 'Diachronic_sub-database' /'Diachronic_data' / 'Diachronic_character_contextual_diversities.csv'
    result_df.to_csv(output_file, index=False)


def generate_diachronic_character_phonology():
    dynasties = ['Tang', 'Song', 'Yuan', 'Ming', 'Qing', 'Subtlex']
    # Load the frequency dataframe
    freq_df_path= ROOT.parent /'Diachronic_sub-database' / 'Diachronic_data' /'Diachronic_character_frequencies.csv'
    freq_df = pd.read_csv(freq_df_path)
    # Load the CAPPD dataframe
    cappd = pd.read_csv(ROOT.parent / 'CAPPD.csv')
    char_tone_rhyme = pingshui_dict()
    # Load the Guangyun dataframe
    guangyun = guangyun_data()
    # Get the list of common characters
    common_characters = freq_df['Character']
    # Extract pinyin and gloss from the frequency dataframe
    pinyin = freq_df['pinyin']
    gloss = freq_df['Gloss']
    # Initialize lists to store the extracted data
    psy_tone = []
    psy_rhyme = []
    gy_rhyme = []
    gy_tone= []
    gy_ID=[]
    # Initialize the OpenCC converter for traditional to simplified characters
    converter = OpenCC('s2t')
    # Iterate over the common characters
    for char in common_characters:
        # Find the row in CAPPD that matches the current character
        cappd_row = cappd[cappd['Character'] == char]
        if not cappd_row.empty:
            psy_tone.append('|'.join(char_tone_rhyme[char]['tone']))
            psy_rhyme.append('|'.join(char_tone_rhyme[char]['rhymes']))
        else:
            psy_tone.append(None)
            psy_rhyme.append(None)
        # Find the row in Guangyun that matches the current character
        guangyun_row = guangyun[guangyun['CHARACTER'] == char]
        if guangyun_row.empty:
            traditional_char = converter.convert(char)
            guangyun_row = guangyun[guangyun['CHARACTER'] == traditional_char]
        if not guangyun_row.empty:
            gy_id=guangyun_row['CHARACTER_ID'].values[0]
            gyr=guangyun_row['RHYME_ID'].values[0]
            gy_rhyme.append(gyr)
            gy_ID.append(gy_id)

            if gyr[:2] in ['sp','xp']:
                gy_tone.append('level')
            else:
                gy_tone.append('oblique')
        else:
            # If the character is not found, append None or a default value
            gy_rhyme.append(None)
            gy_tone.append(None)
            gy_ID.append(None)

    # Create a new dataframe with the extracted data
    new_df = pd.DataFrame({
        'Character': common_characters,
        'Pinyin': pinyin,
        'PSY_Tone': psy_tone,
        'PSY_Rhyme': psy_rhyme,
        'GY_Tone': gy_tone,
        'GY_Rhyme': gy_rhyme,
        'GY_ID': gy_ID,
        'Gloss': gloss
    })

    save_path= ROOT.parent / 'Diachronic_sub-database'/ 'Diachronic_data' / 'Diachronic_Character_Phonology.csv'
    new_df.to_csv(save_path, index=False)

    return new_df




def generate_co_occurrence_matrix():
    chinese_pattern = re.compile(r'[^\u4e00-\u9fa5]')
    dynasties = [ 'Tang', 'Song', 'Yuan', 'Ming','Qing']

    for dy in dynasties:
        print(dy+' is processing')
        dy_vocab_path=OUTPUT / f'Char_vocab_{dy}.csv'
        vocab_df = pd.read_csv(dy_vocab_path)

        filtered_vocab_df = vocab_df[vocab_df["Frequency"] > 10]

        characters = filtered_vocab_df["Character"].tolist()

        co_occurrence_matrix = pd.DataFrame(
            data=np.zeros((len(characters), len(characters)), dtype=int),
            index=characters,
            columns=characters
        )

        dir_path = CORPUS / 'dynasty_corpus' / f'{dy}.csv'

        each_dy_poems = pd.read_csv(dir_path)
        for _, row in each_dy_poems.iterrows():
            text = str(row["内容"])
            for i in range(len(text) - 1):
                first_char = text[i]
                second_char = text[i + 1]

                if first_char in characters and second_char in characters:
                    co_occurrence_matrix.loc[first_char, second_char] += 1


        save_path= ROOT.parent / 'Diachronic_sub-database' / 'bigram_cooccurrence_matrices' / f'co_occurrence_{dy}.csv'
        co_occurrence_matrix.to_csv(save_path)
        print(dy + ' now has been saved to csv file ')

if __name__=="__main__":
    # generate_dynasty_char_vocab()
    # generate_diachronic_characters_frequency()
    # generate_diachronic_diversity()
    generate_diachronic_character_phonology()
    # generate_co_occurrence_matrix()





