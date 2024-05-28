import streamlit as st

from utils import files_processor
from utils import acc_fun

def render_acc():
    st.title('아시아문화전당 자동화 페이지')
    uploaded_file = st.file_uploader("파일을 Drag&Drop으로 업로드 해주세요(:red[단일 파일]의 :red[.docx] 확장자만 지원됩니다.)", type=["docx"], accept_multiple_files=False)

    if uploaded_file is not None:
        file_info = files_processor.get_file_info(uploaded_file)
        if st.button('Run Automation'):
            with st.spinner("The program is in progress. Please do not manipulate other elements while it's running...."):
                result_df = acc_fun.run_acc(
                    uploaded_file=uploaded_file, 
                )
                st.dataframe(result_df)
            download_link = files_processor.get_df_download_link(result_df,  file_info['name']+'_voacb', '.xlsx')
            st.markdown(download_link, unsafe_allow_html=True)