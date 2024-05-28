import streamlit as st
import pandas as pd 
from utils import files_processor
from utils import apply_vocab

def render_apply_vocab():
    st.title('Apply Vocab')
    uploaded_file = st.file_uploader("용어집을 적용할 파일을 Drag&Drop으로 업로드 해주세요(:red[단일 파일]의 :red[.xlsx, .csv, .rtf] 확장자만 지원됩니다.)", type=["csv", "xlsx", "rtf"], accept_multiple_files=False)

    if uploaded_file is not None:
        xlsx_file_info = files_processor.get_file_info(uploaded_file)
        if xlsx_file_info['exntension'] == 'rtf':
            st.warning('rtf 파일은 준비중 입니다.')

        else:
            column_to_process = st.selectbox('용어집을 적용할 컬럼을 선택하세요.:', xlsx_file_info['columns'])
            vocab_file = st.file_uploader("용어집 파일을 Drag&Drop으로 업로드 해주세요(:red[단일 파일]의 :red[.xlsx, .csv] 확장자만 지원됩니다.)", type=["csv", "xlsx"], accept_multiple_files=False)
            if vocab_file:
                vocab_file_info = files_processor.get_file_info(vocab_file)
                col1, col2 = st.columns(2)
                src_column = col1.selectbox('용어집의 출발어를 선택하세요.', vocab_file_info['columns'])
                trg_column = col2.selectbox('용어집의 도착어를 선택하세요.', [col for col in vocab_file_info['columns'] if col != src_column])

                # process_vocabulary 함수 실행
                if st.button('Run Automation'):
                    with st.spinner("The program is in progress. Please do not manipulate other elements while it's running...."):
                        output = apply_vocab.process_vocabulary(xlsx_file_info['dataframe'], column_to_process, vocab_file_info['dataframe'], src_column, trg_column)

                    # st.write(output.head())
                    download_link = files_processor.get_df_download_link(output, xlsx_file_info['name'], '.xlsx')
                    st.markdown(download_link, unsafe_allow_html=True)