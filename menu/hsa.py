import streamlit as st

from utils import hsa
from utils import files_processor
import pandas as pd

def render_split_docs():
    # part1 양단편집
    st.title('HSA 용어집 검수 자동화')
    st.markdown('## #1 양단 편집')
    st.markdown('- Source 파일과 Target 파일을 업로드하면 두파일을 기준으로 양단편집 문서를 생성합니다.')
    st.markdown('- 양단 편집이 완료 된 후 다음 프로세스를 진행해주세요.')

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Source 파일")
        uploaded_file_src = st.file_uploader("Source 파일을 Drag&Drop으로 업로드 해주세요(:red[단일 파일]의 :red[.docx] 확장자만 지원됩니다.)", type=["docx"], accept_multiple_files=False, key="src")
    with col2:
        st.markdown("### Target 파일")
        uploaded_file_trg = st.file_uploader("Target 파일을 Drag&Drop으로 업로드 해주세요(:red[단일 파일]의 :red[.docx] 확장자만 지원됩니다.)", type=["docx"], accept_multiple_files=False, key="trg")
            
    if uploaded_file_src is not None and uploaded_file_trg is not None:
        if st.button('양단편집 실행'):
            with st.spinner('양단편집 실행 중...'):
                src_list = hsa.extract_text_from_file(uploaded_file_src)
                trg_list = hsa.extract_text_from_file(uploaded_file_trg)
                df = hsa.process_document_alignment(src_list, trg_list)
                download_link = files_processor.get_df_download_link(df, '양단편집', '.xlsx')
                st.markdown(download_link, unsafe_allow_html=True)

def render_check_vocab():
    st.markdown('---')
    # part2 번역 용어 찾기
    st.markdown('## #2 용어집 확인')
    st.markdown('- 용어집 파일(.xlsx)와 양단편집이 완료된 파일(.xlsx)를 업로드합니다.')

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 양단편집 완료 파일")
        uploaded_aligned_file = st.file_uploader("양단편집 완료 파일을 업로드 해주세요(:red[단일 파일]의 :red[.xlsx] 확장자만 지원됩니다.)", type=["xlsx"], key="aligned")

    with col2:
        st.markdown("### 용어집 파일")
        uploaded_vocab_file = st.file_uploader("용어집 파일을 업로드 해주세요(:red[단일 파일]의 :red[.xlsx] 확장자만 지원됩니다.)", type=["xlsx"], key="vocab")

    if uploaded_aligned_file is not None and uploaded_vocab_file is not None:
        aligned_df = pd.read_excel(uploaded_aligned_file)
        vocab_df = pd.read_excel(uploaded_vocab_file)
        
        aligned_col_names = aligned_df.columns.tolist()
        vocab_col_names = vocab_df.columns.tolist()
        
        with col1:
            selected_aligned_src_col = st.selectbox('양단편집 파일의 Source 컬럼을 선택해주세요', aligned_col_names, key='aligned_src_col')
            selected_aligned_trg_col = st.selectbox('양단편집 파일의 Target 컬럼을 선택해주세요', aligned_col_names, key='aligned_trg_col')

        with col2:
            selected_vocab_src_col = st.selectbox('용어집 파일의 Source 컬럼을 선택해주세요', vocab_col_names, key='vocab_src_col')
            selected_vocab_trg_col = st.selectbox('용어집 파일의 Target 컬럼을 선택해주세요', vocab_col_names, key='vocab_trg_col')
                
        if st.button('번역 용어 찾기'):
            with st.spinner('번역 용어 찾기 작업을 수행합니다...'):
                # 선택한 컬럼 이름 변경
                aligned_df = aligned_df.rename(columns={selected_aligned_src_col: 'source', selected_aligned_trg_col: 'target'})
                vocab_df = vocab_df.rename(columns={selected_vocab_src_col: 'source', selected_vocab_trg_col: 'target'})

                # 선택한 컬럼의 값을 string 타입으로 변환
                aligned_df['source'] = aligned_df['source'].astype(str)
                aligned_df['target'] = aligned_df['target'].astype(str)
                vocab_df['source'] = vocab_df['source'].astype(str)
                vocab_df['target'] = vocab_df['target'].astype(str)
                
                result, combined_vocab_result = hsa.process_vocab_detection(aligned_df, vocab_df)
                result_download_link = hsa.get_download_link(result, '번역된 용어 찾기 결과', '.xlsx', '번역된 용어 찾기 결과 다운로드')
                st.markdown(result_download_link, unsafe_allow_html=True)
                combined_vocab_result_download_link = hsa.get_download_link(combined_vocab_result, '용어 전체 취합', '.xlsx', '추출 용어 다운로드')
                st.markdown(combined_vocab_result_download_link, unsafe_allow_html=True)