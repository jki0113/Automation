print("ㅡㅡㅡstreamlit realoadedㅡㅡㅡ")
from dotenv import load_dotenv
import os
load_dotenv()

import streamlit as st
from streamlit_option_menu import option_menu

from assets import display as dp

from menu import LKH
from menu import prompt_test
from menu import gpt_excel_automation
from menu import language_extraction
from menu import differences_comparsion
from menu import word_count
from menu import apply_vocab
from menu import acc
from menu import hsa

import pandas as pd
import random

with st.sidebar:
    selected = option_menu(
        "Automation menu", 
        [
            'Home', 
            'Prompt Test',
            'GPT Excel Automation',
            "Language Extraction", 
            'Differences Comparsion', 
            'Word Count', 
            'Apply Vocab',
            'ACC Automation', 
            'HSA', # 선아씨(+윤국 씨) 자동화 요청
            'LKH', # 세계법제처
        ], 
        icons=[
            "house", 
            "cloud-upload", 
            "cloud-upload", 
            "cloud-upload", 
            "cloud-upload", 
            "cloud-upload", 
            "cloud-upload", 
            "cloud-upload",
            "cloud-upload",
            "cloud-upload",
        ], 
        menu_icon="option", 
        default_index=0
    )

# 홈 메뉴
if selected == "Home":
    dp.home()

# 프롬프트 테스트 페이지
elif selected=='Prompt Test':
    prompt_test.render_prompt_test()

# 엑셀 gpt 자동화
elif selected == "GPT Excel Automation":
    # 엑셀 gpt 자동화 기능 실행
    gpt_excel_automation.render_gpt_excel_automation()
    # 협업 요청 이메일 보내기
    gpt_excel_automation.render_request_collab()

# 언어추출
elif selected == "Language Extraction":
    language_extraction.render_language_extraction()

# 다른 부분 색칠 표시 + 변경률 표시
elif selected == 'Differences Comparsion':
    differences_comparsion.render_diff_comparsion()

elif selected == 'Word Count':
    word_count.render_word_count()

elif selected == 'Apply Vocab':
    apply_vocab.render_apply_vocab()

elif selected=='ACC Automation':
    acc.render_acc()

elif selected=='HSA':
    hsa.render_split_docs()
    hsa.render_check_vocab()

elif selected=='LKH':
    LKH.render_page()
