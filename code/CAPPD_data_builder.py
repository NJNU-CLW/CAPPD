import math
from utils import *
import re
from config import *

cedict = load_char_def()
def clean_text(text):
    cleaned_text = re.sub(r'[^\u4e00-\u9fff]', '', text)
    return cleaned_text

# Initialize dictionaries to store character frequency and contextual diversity
char_frequency = defaultdict(int)
char_contextual_diversity = defaultdict(set)

folder_path = CORPUS/'raw_corpus'
if folder_path.exists():
    paths=list(folder_path.iterdir())
    for filename in paths :
        if filename.suffix =='.csv':
            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path, encoding='utf-8')
            # Iterate through each row in the content column
            for content in df['内容']:
                cleaned_content = clean_text(content)
                # Tokenize by character
                for char in cleaned_content:
                    char_frequency[char] += 1
                    char_contextual_diversity[char].add(content)

total_characters = sum(char_frequency.values())
stroke_dict=get_stroke_count()
radical_dict=get_radical()
total_poems_num=781193
result_data = {
    'Character': [],
    'Pinyin':[],
    'Frequency': [],
    'Log_frequency': [],
    'Frequency_per_million': [],
    'CD': [],
    'Log_CD': [],
    'CD%':[],
    'Strokes': [],
    'Radical': [],
    'Gloss':[]
}

for char, freq in char_frequency.items():
    result_data['Character'].append(char)
    result_data['Pinyin'].append(get_pinyin(char))
    result_data['Frequency'].append(freq)
    result_data['Log_frequency'].append(math.log(freq,10) if freq > 0 else 0)
    result_data['Frequency_per_million'].append((freq / total_characters) * 1e6)
    result_data['CD'].append(len(char_contextual_diversity[char]))
    result_data['Log_CD'].append(math.log(len(char_contextual_diversity[char]),10) if len(char_contextual_diversity[char]) > 0 else 0)
    result_data['CD%'].append(len(char_contextual_diversity[char])/total_poems_num if len(char_contextual_diversity[char]) > 0 else 0)
    result_data['Strokes'].append(stroke_dict.get(char,-1))
    result_data['Radical'].append(radical_dict.get(char, -1))
    result_data['Gloss'].append(cedict.get(char,'-'))

if __name__ == "__main__":
    result_df = pd.DataFrame(result_data)
    df_sorted = result_df.sort_values(by='Frequency', ascending=False)
    df_sorted.to_csv(ROOT.parent/'CAPPD.csv', index=False, encoding='utf-8-sig')
    print("The CAPPD corpus has been generated and saved to 'CAPPD.csv'.")