# 세계 법제처
# 담당 PL 임경화

import streamlit as st
from utils.docx_processor import *
from utils.files_processor import *
from utils.numeric_comparsion import *
from utils.legislative_automation import *

def render_page():
    st.title('LKH 법률문서 자동화')
    st.markdown('---')
    split_doc()
    st.markdown('---')
    legislative_automation()
    st.markdown('---')
    result_validation()
    st.markdown('---')

def split_doc():
    # part1 양단편집
    st.markdown('## #1 양단 편집')
    st.markdown('- 양단으로 편집된 .docx 파일을 업로드 하세요. (단일 파일 지원)')
    st.markdown('- 양단 편집이 완료 된 후 다음 프로세스를 진행해주세요.')

    st.markdown("### Source 파일")
    source_docx_sbs = st.file_uploader("Source 파일을 Drag&Drop으로 업로드 해주세요(:red[단일 파일]의 :red[.docx] 확장자만 지원됩니다.)", type=["docx"], accept_multiple_files=False, key="source_docx_sbs")
    if source_docx_sbs is not None:
        if st.button('양단편집 실행'):
            with st.spinner('양단편집 실행 중...'):
                file_info = get_file_info(source_docx_sbs)
                print(file_info)
                para_list = extract_and_split_text_from_docx(source_docx_sbs)
                result_df = convert_two_column_excel_from_lists(para_list)
                """여기에 결과 데이터프레임을 엑셀로 변환해주는 코드를 작성"""
                df_download_link = get_df_download_link(result_df, f"{file_info['name']}_result", ".xlsx")
                st.markdown(df_download_link, unsafe_allow_html=True)

def legislative_automation():
    # part2 조문체계 처리 자동화
    st.markdown('## #2 조문체계 처리 자동화')
    source_xlsx_legislative = st.file_uploader("Source 파일을 Drag&Drop으로 업로드 해주세요(:red[단일 파일]의 :red[.xlsx] 확장자만 지원됩니다.)", type=["xlsx"], accept_multiple_files=False, key="source_xlsx_legislative")
    if source_xlsx_legislative is not None:
        file_info = get_file_info(source_xlsx_legislative)
        df = file_info['dataframe']

        # 자동화 컬럼 선택
        selected_col = st.selectbox('자동화할 컬럼을 선택하세요:', file_info["columns"], key="selected_column")
        # 어떤 국가의 법령인지 선택
        country_options = [
            "미국", 
            "호주", 
            "싱가포르", 
            "영국", 
            "캐나다", 
            "케냐", 
            "스리랑카", 
            "뉴질랜드", 
            "인도", 
            "유럽연합", 
            "캄보디아", 
            "필리핀", 
            "말레이시아"
        ]
        selected_country = st.selectbox('적용할 국가를 선택하세요:', country_options, key="selected_country")

        if st.button('run automation'):
            st.write(f"선택된 컬럼: {selected_col}, 적용할 국가: {selected_country}")
            result = run_legislative_automation(df, selected_col, selected_country)
            df_download_link = get_df_download_link(result, f"{file_info['name']}_result", ".xlsx")
            st.markdown(df_download_link, unsafe_allow_html=True)


def result_validation():
    # part3 숫자 검증처리 자동화
    st.markdown('## #3 숫자 검증처리 자동화')
    st.markdown('- 양단으로 구성된 .xlsx 파일을 업로드 하세요. (단일 파일 지원)')
    source_xlsx_num = st.file_uploader("숫자를 비교 할 파일을 Drag&Drop으로 업로드 해주세요(:red[단일 파일]의 :red[.xlsx, .xls, .csv] 확장자만 지원됩니다.)", type=["xlsx", "csv", "xls"], accept_multiple_files=False, key="source_xlsx_num")
    if source_xlsx_num is not None:
        file_info = get_file_info(source_xlsx_num)
        df = file_info['dataframe']
        col1, col2 = st.columns(2)
        selected_col1 = col1.selectbox("첫 번째 컬럼을 선택하세요: ", file_info['columns'])
        selected_col2 = col2.selectbox("두 번째 컬럼을 선택하세요: ", [col for col in file_info['columns'] if col != selected_col1])
        if st.button('숫자비교 실행'):
            with st.spinner("숫자비교 실행 중..."):
                df[f'{selected_col1}-{selected_col2}'] = df.apply(lambda row: check_translation_numbers(row[f'{selected_col1}'], row[f'{selected_col2}']), axis=1)
                df[f'{selected_col2}-{selected_col1}'] = df.apply(lambda row: check_translation_numbers(row[f'{selected_col2}'], row[f'{selected_col1}']), axis=1)
                result = apply_number_style_formatter(df, [f'{selected_col1}',f'{selected_col2}'])
                download_link = get_worksheet_download_link(result)
                st.markdown(download_link, unsafe_allow_html=True)


