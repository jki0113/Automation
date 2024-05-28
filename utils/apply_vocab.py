import re
from tqdm import tqdm
import pandas as pd
import streamlit as st
from stqdm import stqdm
def generate_ngrams(text, n):
    """n-gram 생성 함수"""
    text = str(text)
    words = text.split()
    ngrams = []
    for i in range(len(words) - n + 1):
        ngrams.append(' '.join(words[i:i+n]))
    return ngrams

def preprocess_text(text):
    """특수문자 제거 및 소문자 변환"""
    return re.sub(r'[^a-zA-Z0-9\s]', ' ', text)

def process_vocabulary(df, src_df, vocab, src_vocab, trg_vocab):
    vocab_str_list = []

    for idx in stqdm(range(df.shape[0])):
        vocab_tmp = ""
        processed_sentence = preprocess_text(str(df[src_df][idx]))
        original_sentence = df[src_df][idx]

        ngrams_in_sentence = []
        for n in range(1, 6):  # 1~5gram
            ngrams_in_sentence.extend(generate_ngrams(processed_sentence, n))
            ngrams_in_sentence.extend(generate_ngrams(original_sentence, n))
        ngrams_in_sentence = list(set(ngrams_in_sentence))
        
        for idx, vocab_idx in enumerate(range(vocab.shape[0])):

            word_en = str(vocab[src_vocab][vocab_idx]).strip()
            word_ko = str(vocab[trg_vocab][vocab_idx]).strip()

            matched = any([ng.lower().startswith(word_en.lower()) for ng in ngrams_in_sentence])
            if matched:
                vocab_tmp += f"{word_en} : {word_ko}\n"

        vocab_str_list.append(vocab_tmp.strip())

    df['apply_vocab'] = vocab_str_list
    return df

import streamlit as st
import pandas as pd
import os
import re

def char_to_value(char):
    unicode_value = ord(char)
    converted_value = unicode_value - 65536 if unicode_value > 32767 else unicode_value
    return converted_value

def value_to_char(converted_value):
    unicode_value_reverted = converted_value + 65536 if converted_value < 32768 else converted_value
    char_reverted = chr(unicode_value_reverted)
    return char_reverted

def text_inputer(text):
    pattern = r'[a-z|A-Z| ]'
    template = "{{\\f97\\uc0\\u{} }}"
    result_chat = ''
    for char in text:
        if re.match(pattern, char):
            result_chat += char
        else:
            value = char_to_value(char)
            formatted_string = template.format(value)
            result_chat += formatted_string
    return result_chat

def process_rtf_file(uploaded_rtf_file, vocab_dataframe, vocab_column_name):
    rtf_content = uploaded_rtf_file.getvalue().decode('utf-8')
    texts = list(vocab_dataframe[vocab_column_name])
    texts = texts[::-1]

    # Extracting positions where changes should be made
    pattern = r'{\\rtlch\\fcs1 \\ltrch\\fcs0\\noproof \\cell }'
    index_list = [match.span() for match in re.finditer(pattern, rtf_content)]
    index_list = index_list[::-1]

    for i, index_set in enumerate(index_list):
        rtf_content = rtf_content[:index_set[0]+33] + text_inputer(texts[i]) + rtf_content[index_set[0]+33:]

    return rtf_content