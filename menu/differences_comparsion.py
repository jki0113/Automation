import streamlit as st
from utils import differences_comparsion
from utils import files_processor

def render_diff_comparsion():
    st.title('Differences Comparsion')
    st.markdown('---')
    uploaded_file = st.file_uploader("자동화 할 파일을 Drag&Drop으로 업로드 해주세요(:red[단일 파일]의 :red[.xlsx, .csv] 확장자만 지원됩니다.)", type=["csv", "xlsx"], accept_multiple_files=False)

    if uploaded_file is not None:
        file_info = files_processor.get_file_info(uploaded_file)

        col1, col2 = st.columns(2)

        selected_col1 = col1.selectbox("첫 번째 컬럼을 선택하세요: ", file_info['columns'])
        selected_col2 = col2.selectbox("두 번째 컬럼을 선택하세요: ", [col for col in file_info['columns'] if col != selected_col1])

        if st.button('Run Automation'):
            with st.spinner("The program is in progress. Please do not manipulate other elements while it's running...."):
                output = differences_comparsion.find_diff(uploaded_file, file_info['extension'], selected_col1, selected_col2)

                download_link = files_processor.get_worksheet_download_link(output, f"{file_info['name']}_result.xlsx")
                st.markdown(download_link, unsafe_allow_html=True)