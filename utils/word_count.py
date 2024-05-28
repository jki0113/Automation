from tqdm import tqdm
import streamlit as st
import os
import subprocess
import re
import unicodedata
from ftlangdetect import detect as lang_detector
import docx
import PyPDF2
from io import BytesIO
from typing import Union
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
import pandas as pd
try:
    from konlpy.tag import Mecab
except:
    from eunjeon import Mecab
from collections import Counter, defaultdict
from stqdm import stqdm
import fitz

def clean_text(data):
    # 유니코드 이스케이프 시퀀스를 제거
    data = re.sub(r'\\x[0-9a-fA-F]{2}', '', data)
    # 줄바꿈, 탭 문자 등을 제거
    data = data.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    # 유니코드 문자를 처리
    data = ''.join([c for c in data if not unicodedata.category(c).startswith('C')])
    return data

def detect_lang(clean_text):
    # 패스트 텍스트는 입력시 줄바꿈 나면 에러 생김으로 처리
    clean_text = clean_text.replace('\n', '')
    lang_detect = lang_detector(
        text = clean_text,
        low_memory = False,
    )
    return lang_detect['lang']

def hwp2text(filename):
    import olefile
    import zlib
    import struct
    f = olefile.OleFileIO(filename)
    dirs = f.listdir()

    # HWP 파일 검증
    if ["FileHeader"] not in dirs or \
       ["\x05HwpSummaryInformation"] not in dirs:
        raise Exception("Not Valid HWP.")

    # 문서 포맷 압축 여부 확인
    header = f.openstream("FileHeader")
    header_data = header.read()
    is_compressed = (header_data[36] & 1) == 1

    # Body Sections 불러오기
    nums = []
    for d in dirs:
        if d[0] == "BodyText":
            nums.append(int(d[1][len("Section"):]))
    sections = ["BodyText/Section"+str(x) for x in sorted(nums)]

    # 전체 text 추출
    full_text = ""
    for section in sections:
        bodytext = f.openstream(section)
        data = bodytext.read()
        if is_compressed:
            unpacked_data = zlib.decompress(data, -15)
        else:
            unpacked_data = data
    
        # 각 Section 내 text 추출    
        section_text = ""
        i = 0
        size = len(unpacked_data)
        while i < size:
            header = struct.unpack_from("<I", unpacked_data, i)[0]
            rec_type = header & 0x3ff
            rec_len = (header >> 20) & 0xfff

            if rec_type in [67]:
                rec_data = unpacked_data[i+4:i+4+rec_len]
                section_text += rec_data.decode('utf-16')
                section_text += "\n"

            i += 4 + rec_len

        full_text += section_text
        full_text += "\n"

    return full_text
def docx2text(file_path):
    # .docx 파일 열기
    doc = docx.Document(file_path)

    # .docx 파일에서 모든 텍스트 추출
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)

    # 텍스트 리스트를 하나의 문자열로 변환하여 반환
    full_text = ' '.join(full_text)

    return full_text

def pdf2text(file_or_bytes: Union[str, BytesIO]):
    # PyMuPDF 사용
    if isinstance(file_or_bytes, str):
        # file_or_bytes is a file path
        pdf_document = fitz.open(file_or_bytes)
    else:
        # file_or_bytes is a BytesIO object
        file_or_bytes.seek(0)  # reset the position to the start
        pdf_document = fitz.open(stream=file_or_bytes.read(), filetype="pdf")
    
    full_text = ""
    
    total_pages = len(pdf_document)
    for page in pdf_document:
        full_text += page.get_text()

    pdf_document.close()
    
    return full_text


def txt2text(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        # 파일에서 텍스트를 읽어옵니다.
        full_text = file.read()
    return full_text

def generate_ngrams(words, n):
    ngrams = zip(*[words[i:] for i in range(n)])
    return [" ".join(ngram) for ngram in ngrams]

def en_preprocessing(text):
    words = word_tokenize(text)
    words = [word.lower() for word in words]
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words]
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word.isalnum() and word not in stop_words]

    word_counts = defaultdict(int)
    for n in stqdm(range(1, 3 + 1)):  # 3-gram까지만 고려
        ngrams = generate_ngrams(words, n)
        for ngram in ngrams:
            word_counts[ngram] += 1

    dataframe = pd.DataFrame(word_counts.items(), columns=['word', 'frequency'])
    dataframe = dataframe.sort_values(by='frequency', ascending=False)

    return dataframe

def ko_preprocessing(text):
    mecab = Mecab()
    words = mecab.morphs(text)  # 형태소 단위로 분리
    words = mecab.pos(text)
    usedPOS = ['NNG', 'NNP', 'NP', 'VV', 'VA', 'XR', 'SL', 'MAG']
    words = [word for word, pos in words if pos in usedPOS]
    word_counts = defaultdict(int)
    for n in stqdm(range(1, 3 + 1)):  # 3-gram까지만 고려
        ngrams = generate_ngrams(words, n)
        for ngram in ngrams:
            word_counts[ngram] += 1

    dataframe = pd.DataFrame(word_counts.items(), columns=['word', 'frequency'])
    dataframe = dataframe.sort_values(by='frequency', ascending=False)

    return dataframe

def other_languages(text):
    words = text.split()
    words = generate_ngrams(words, 3)
    word_count = Counter(words)
    df = pd.DataFrame.from_dict(word_count, orient='index', columns=['frequency'])
    df.index.name = 'word'
    df.sort_values('frequency', ascending=False, inplace=True)
    dataframe = df.reset_index()    
    return dataframe

def wordCount(file, extension):
    if extension == '.hwp':
        full_text = clean_text(hwp2text(file))
    elif extension == '.docx':
        full_text = clean_text(docx2text(file))
    elif extension == '.pdf':
        full_text = clean_text(pdf2text(file))
    elif extension == '.txt':
        full_text = clean_text(txt2text(file))

    lang = detect_lang(full_text)
    if lang == 'ko':
        """한글 전처리 프로세스""" 
        try:
            result = ko_preprocessing(full_text)
            print('mecab 작동')
        except:
            result = other_languages(full_text)
            print('mecab 실패 -> other_languages(full_text)')
        
    elif lang == 'en':
        """영어 전처리 프로세스"""   
        result = en_preprocessing(full_text)
    else:
        """처리해주기 어려운 언어로 그냥 띄어쓰기 기준으로 해줄 것"""
        result = other_languages(full_text)

    return result

