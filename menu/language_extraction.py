import streamlit as st
from utils import language_extraction
from utils import files_processor

def render_language_extraction():
    st.title("Language Extraction")   
    st.markdown('---')
    uploaded_file = st.file_uploader("자동화 할 파일을 Drag&Drop으로 업로드 해주세요(:red[단일 파일]의 :red[.xlsx, .csv] 확장자만 지원됩니다.)", type=["csv", "xlsx"], accept_multiple_files=False)
    if uploaded_file is not None:
        file_info = files_processor.get_file_info(uploaded_file)
        selected_column = st.selectbox("언어를 예측할 컬럼을 입력해주세요.: ", file_info['columns'])

        threshold = st.slider("임계값(%) 설정: :red[*모델이 설정한 임계 값 이하로 예측될 경우 'UNK'를 반환합니다.] ", 0, 100 ,40)
        if st.button("Run Automation"):
            with st.spinner("The program is in progress. Please do not manipulate other elements while it's running...."):
                result = language_extraction.extract_lang(uploaded_file, file_info['extension'], selected_column, threshold)
            # st.dataframe(result.head(), height=1000)
            # st.markdown(fn.get_csv_download_link(result), unsafe_allow_html=True)
            st.markdown(files_processor.get_df_download_link(result, file_info['name'], file_info['extension']), unsafe_allow_html=True)