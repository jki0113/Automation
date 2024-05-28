import pandas as pd
import warnings
warnings.filterwarnings('ignore')
import re
import opencc
from ftlangdetect import detect as lang_detector
from tqdm import tqdm
import streamlit as st
from stqdm import stqdm

def extract_lang(file, extension, column, threshold):
    print(threshold)
    DATAFRAME = pd.read_excel(file) if extension == '.xlsx' else pd.read_csv(file, encoding='utf-8-sig')
    COLUMN = column
    THRESHOLD = threshold

    DATAFRAME = DATAFRAME[[COLUMN]]
    DATAFRAME['lang_detect'] = ''
    DATAFRAME['score'] = .0
    DATAFRAME.fillna('', inplace=True)


    for idx in stqdm(range(DATAFRAME.shape[0])):

        clean_text = str(DATAFRAME[COLUMN][idx]).replace('\n', '') # 줄바꿈 에러 방지
        lang_detect = lang_detector(
            text = clean_text,
            low_memory = False,
        )
        lang = lang_detect['lang']
        score = round(float(lang_detect['score']), 2) * 100

        # score 값이 임계 값 보다 낮은 경우 잘못된 경우가 있을 수 있기 때문에 UNK 처리
        if score < THRESHOLD:
            DATAFRAME['lang_detect'][idx] = 'UNK'
            DATAFRAME['score'][idx] = .0

        # 임계 값 보다 크면서 중국어일 경우 번체 간체 검사
        elif score > THRESHOLD and lang == 'zh':
            converter = opencc.OpenCC('t2s') # 문장을 간체에서 번체로 변환
            pattern = r'[^\u4e00-\u9fff]' # 정확한 비교를 위해 문자를 제외한 나머진 제거 후 처리
            clean_text = re.sub(pattern, '', clean_text)    
            converted_text = converter.convert(clean_text)

            if converted_text == clean_text:
                DATAFRAME['lang_detect'][idx] = 'zh-cn'
            else:
                DATAFRAME['lang_detect'][idx] = 'zh-tw'

        # 임계 값 보다 크면서 중국어 아닐 경우
        else:
            DATAFRAME['lang_detect'][idx] = lang
        
        DATAFRAME['score'][idx] = score
    return DATAFRAME

