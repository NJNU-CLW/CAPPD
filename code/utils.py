import pandas as pd
import os, re, json, urllib.request, zipfile, io
import pypinyin
from pypinyin import lazy_pinyin
from opencc import OpenCC
from config import *
from collections import defaultdict
cc=OpenCC('t2s')
_UNIHAN_DICT_PATH =SOURCE/ 'unihan_def.json'


def get_pinyin(char: str) -> str:
    """Returns the pinyin for a singl e Chinese character or multiple characters, with tone numbers."""
    return " ".join(lazy_pinyin(char, style=pypinyin.TONE))

def load_char_def(cache_path=_UNIHAN_DICT_PATH):
    # =============================================================================
    # Character Translation (Chinese–English mapping)
    # =============================================================================
    # Source: Unihan.zip from Unicode Character Database (UCD)
    # Official URL: https://www.unicode.org/Public/UCD/latest/ucd/
    # License: Unicode License (permissive, allows redistribution with attribution)
    #
    # Note for users:
    # 1. Download the Unihan.zip file manually from the official Unicode website.
    # 2. Extract the archive, which contains multiple tab-delimited text files (Unihan_Readings.txt).
    # 3. Place the extracted file under `source/`.
    # 4. This script uses these files as a Chinese-to-English dictionary for
    #    the "Gloss" column.
    """Chinese →English（Unihan kDefinition）"""
    if os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    char_def = {}
    unihan_path=SOURCE/'Unihan_Readings.txt'
    with open(unihan_path, encoding='utf-8') as f:
        for line in f:
            m = re.match(r'U\+([0-9A-F]+)\tkDefinition\t(.+)', line)
            if m:
                char = chr(int(m.group(1), 16))
                defn = m.group(2).split(';')[0].strip()
                char_def[char] = defn

    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(char_def, f, ensure_ascii=False, indent=0)
    return char_def


def guangyun_data():

# =============================================================================
# GY_RHYME data (Guangyun rhymes)
# =============================================================================
# Source: guangyun_new.tsv from the Fanqie dataset (Li et al., 2024)
#         Available at Zenodo (DOI: 10.5281/zenodo.10828130)
# License: [check Zenodo record, typically CC-BY]
#
# Note for users:
# 1. Download the archive `fanqie-0.1.zip` from the Zenodo DOI above.
# 2. Extract the archive. The file of interest is located at:
#       raw/guangyun_new.tsv
# 3. Place this file under the local path:
#       source/guangyun_new.tsv
    path=SOURCE / 'guangyun_new.tsv'
    guangyun_data = pd.read_csv(path, sep='\t')
    return guangyun_data

def rhyme_to_id(rhyme_str: str) -> str:
    """
    Mapping Rhyme to RHYME_ID

    """
    tone_map = {'上平聲': 'sp', '下平聲': 'xp', '上聲': 's', '去聲': 'q', '入聲': 'r'}
    ids = []
    m = re.match(r'(上平聲|下平聲|上聲|去聲|入聲)\s*([〇一二三四五六七八九十]+)\s*[\u4e00-\u9fff]*', rhyme_str)
    if not m:
        return ''
    tone_zh, num_zh = m.groups()

    num = chinese_to_arabic(num_zh)
    ids.append(f'{tone_map[tone_zh]}{num}')

    return ','.join(ids)


def chinese_to_arabic(s: str) -> int:

    cn = '〇一二三四五六七八九十'
    d = {c: i for i, c in enumerate(cn)}

    if s.startswith('十') and len(s) == 1:
        return 10
    if s.startswith('十') and len(s) == 2:
        return 10 + d[s[1]]
    if s.endswith('十') and len(s) == 2:
        return d[s[0]] * 10
    if len(s) == 3 and s[1] == '十':
        return d[s[0]] * 10 + d[s[2]]
    else:
        n = d.get(s, 0)

    return f'{n:02d}'


def pingshui_dict():

    # =============================================================================
    # PSY_Rhyme and Tone data (Pingshui rhyme categories)
    # =============================================================================
    # Source: 平水韻 (Pingshui Rhyme), Wikisource
    # URL: https://zh.wikisource.org/wiki/平水韻
    # Format: Plain-text file provided by Wikisource (downloadable directly)
    # License: CC BY-SA 3.0
    #
    # Note for users:
    # 1. Download the plain-text version of the page from Wikisource.
    # 2. Save the file under the local path:

    path=SOURCE / '平水韻.txt'

    CHAR_MAP = defaultdict(lambda: {'tone': set(), 'rhymes': set()})

    with open(path, encoding='utf-8') as f:
        txt = f.read()

    blocks = re.split(r'.*?部\n', txt)[1:]
    for block in blocks:
        lines = [L.strip() for L in block.splitlines() if L.strip()]
        if not lines:
            continue
        i = 0
        while i < len(lines):
            title = lines[i]
            i += 1
            rhyme_name=title
            if '平' in rhyme_name:
                tone = 'level'
            elif any(k in rhyme_name for k in ('上', '去', '入')):
                tone = 'oblique'
            else:
                tone = 'Unknown'

            char_list = []
            while i < len(lines) and not re.match(r'[上下]平|上聲|去聲|入聲', lines[i]):
                char_list.extend(lines[i])
                i += 1
            chars_str=''.join(char_list)
            chars=re.sub('【[詞辭]】','',chars_str)

            unique_chars = set()
            for c in chars:
                if '\u4e00' <= c <= '\u9fff':
                    unique_chars.add(c)
                    unique_chars.add(cc.convert(c))

            for ch in unique_chars:

                CHAR_MAP[ch]['tone'].add(tone)
                CHAR_MAP[ch]['rhymes'].add(rhyme_to_id(rhyme_name))
                # CHAR_MAP[ch]['rhymes'].add(rhyme_name)
    f.close()

    return CHAR_MAP


def get_stroke_count():
    """
    Retrieve the stroke count of a given Chinese character from a specified text file.
    """
    # =============================================================================
    # Stroke count data (Chinese characters code table)
    # =============================================================================
    # Source: 全部汉字码表.TXT from Chinese-characters-code-table project
    # Archived at Zenodo (DOI: [YOUR_ZENODO_DOI])
    # License: [MIT / CC-BY / etc., check original repo LICENSE]
    #
    # Note for users:
    # 1. Download the dataset manually from the Zenodo DOI above.
    # 2. Place the file under the local path: `data/strokes/全部汉字码表.TXT`
    # 3. The script will read this file to extract stroke counts for characters.
    stroke_file = ROOT / 'source' / '全部汉字码表.TXT'
    stroke_file=open(stroke_file, 'r', encoding='gb18030')
    lines=stroke_file.readlines()

    stroke_dict={}
    for line in lines[6:]:
        columns = line.strip().split(' ')
        columns=[c for c in columns if len(c)!=0]# Split columns by tab
        if len(columns) >= 7:  # Ensure there are at least 7 columns
            character = columns[0]  # The first column is the character
            stroke_count = columns[6]  # The 7th column is the stroke count
            stroke_dict[character]=int(stroke_count)

    return stroke_dict

def get_radical():
    """
    Retrieve the stroke count of a given Chinese character from a specified text file.
    """
    # =============================================================================
    # Stroke count data (Chinese characters code table)
    # =============================================================================
    # Source: 全部汉字码表.TXT from Chinese-characters-code-table project
    # Archived at Zenodo (DOI: [YOUR_ZENODO_DOI])
    # License: [MIT / CC-BY / etc., check original repo LICENSE]
    #
    # Note for users:
    # 1. Download the dataset manually from the Zenodo DOI above.
    # 2. Place the file under the local path: `data/strokes/全部汉字码表.TXT`
    # 3. The script will read this file to extract stroke counts for characters.
    stroke_file = ROOT / 'source' / '全部汉字码表.TXT'
    stroke_file=open(stroke_file, 'r', encoding='gb18030')
    lines=stroke_file.readlines()

    radical_dict={}
    for line in lines[6:]:
        columns = line.strip().split(' ')
        columns=[c for c in columns if len(c)!=0]# Split columns by tab
        if len(columns) >= 7:  # Ensure there are at least 7 columns
            character = columns[0]  # The first column is the character
            radical = columns[7]  # The 7th column is the stroke count
            radical_dict[character]=radical

    return radical_dict
def get_dynasty_corpus():
    folder_path = CORPUS / 'raw_corpus'
    output_path = CORPUS / 'dynasty_corpus'
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    dynasty_map = {
        '唐': 'Tang',
        '宋': 'Song',
        '元': 'Yuan',
        '明': 'Ming',
        '清': 'Qing',
        '辽': 'Song',
        '金': 'Song'
    }

    dynasty_data = {
        'Tang': pd.DataFrame(),
        'Song': pd.DataFrame(),
        'Yuan': pd.DataFrame(),
        'Ming': pd.DataFrame(),
        'Qing': pd.DataFrame()
    }

    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            prefix = filename[0]

            if prefix in dynasty_map:
                dynasty = dynasty_map[prefix]
            else:
                continue


            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path)


            dynasty_data[dynasty] = pd.concat([dynasty_data[dynasty], df])


    for dynasty, df in dynasty_data.items():
        if not df.empty:
            output_filename = output_path / f'{dynasty}.csv'

            df.to_csv(output_filename, index=False)
            print(f'Saved {output_filename}')

if __name__ == "__main__":
    get_dynasty_corpus()