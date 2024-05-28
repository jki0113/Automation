import streamlit as st

from utils import files_processor
from utils import word_count

def render_word_count():
    st.title('Word Count')   
    uploaded_file = st.file_uploader("자동화 할 파일을 Drag&Drop으로 업로드 해주세요(:red[단일 파일]의 :red[.hwp, .pdf, .docx, .txt] 확장자만 지원됩니다.)", type=["hwp", "pdf", "docx", "txt"], accept_multiple_files=False)

    if uploaded_file is not None:
        file_info = files_processor.get_file_info(uploaded_file)

        if st.button('Run Automation'):
            with st.spinner("The program is in progress. Please do not manipulate other elements while it's running...."):
                result = word_count.wordCount(uploaded_file, file_info['extension'])
            st.markdown(files_processor.get_df_download_link(result, file_info['name'], extension='.xlsx'), unsafe_allow_html=True)    