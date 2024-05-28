import streamlit as st
import random

from utils import email
from utils import files_processor
from utils import async_gpt

def render_gpt_excel_automation():
    st.title("GPT Excel Automation")   
    st.markdown("서버 부하 및 비용 효율성을 위해 :red[300row 까지]만 자동화 됩니다. 300row로 테스트 완료 후 대량 요청 처리가 필요한 경우 :red[**'협업 요청하기'**] 버튼을 통해 문의 부탁드립니다.")
    st.markdown('---')
    uploaded_file = st.file_uploader("자동화 할 파일을 Drag&Drop으로 업로드 해주세요(:red[단일 파일]의 :red[.xlsx, .csv] 확장자만 지원됩니다.)", accept_multiple_files=False, type=['xlsx', 'csv'], key='uploader1')
    if uploaded_file is not None:
        # 데이터 프레임으로 파일을 읽어옴
        file_info = files_processor.get_file_info(uploaded_file)
        file_info['dataframe'].fillna('', inplace=True)
        for col in file_info['dataframe'].columns:
            file_info['dataframe'][col] = file_info['dataframe'][col].astype(str)
        columns_str = ' '.join([f":red[**{{{col}}}**], " for col in file_info['columns']])
        
        st.markdown(f"추출된 컬럼을 활용하여 Prompt를 작성해주세요: {columns_str}")

        prompt = st.text_area("Prompt :red[*자동화 할 컬럼의 값은 중괄호 '{}' 로 표시해주세요(예시 참조)]", placeholder="Translate Korean to English:\nsrc: {src}\ntrg: {trg}", key='textarea2')
        
        if 'show_sample' not in st.session_state:
            st.session_state.show_sample = False

        if 'show_gpt_automation_btn' not in st.session_state:
            st.session_state.show_gpt_automation_btn = False

        if st.button('sample prompt') or st.session_state.show_sample:
            if not prompt:
                st.error("Error: The prompt value is missing!")
            else:
                st.session_state.show_sample = True

                sample_prompt = prompt  # sample_prompt 초기화
                dev_prompt = prompt # dev_prompt도 미리 초기화

                matches = async_gpt.get_fstring_from_prompt(prompt) 
                    
                for column_name in matches:
                    if column_name in file_info['dataframe'].columns:
                        random_index = random.randint(0, file_info['dataframe'].shape[0] - 1)
                        value = file_info['dataframe'][column_name].iloc[random_index]

                        check_line_break = value.split('\n')
                        if len(check_line_break) > 1:
                            tmp_check_text = '\n'.join([f':red[{i}]' for i in check_line_break])
                            sample_prompt = sample_prompt.replace(f"{{{column_name}}}", f"{tmp_check_text}")
                        else:
                            sample_prompt = sample_prompt.replace(f"{{{column_name}}}", f":red[{value}]")
                        # dev_prompt = .replace(f"{{{column_name}}}", f"{value}]")

                
                # print(sample_prompt)
                st.markdown(sample_prompt.replace('\n', '\n\n').replace('```', '\```').replace('-', '\-'))
                st.session_state.show_gpt_automation_btn = True

            if st.session_state.show_gpt_automation_btn:
                if st.button('run automation'):
                    prompt_list = []
                    for idx in range(file_info['dataframe'].shape[0]):
                        tmp_prompt = dev_prompt
                        for col_name in matches:
                            if col_name in file_info['dataframe'].columns:
                                value = file_info['dataframe'][col_name].iloc[idx]
                                tmp_prompt = tmp_prompt.replace(f"{{{col_name}}}", str(value))
                        prompt_list.append(tmp_prompt)
                    # for i in prompt_list:
                        # st.markdown(i)
                        # st.markdown('---')
                        # print(i)
                        # print('---')
                    with st.spinner("The program is in progress. Please do not manipulate other elements while it's running...."):
                        result = async_gpt.run_gpt(file_info['dataframe'], prompt_list)
                    st.markdown(files_processor.get_df_download_link(result, file_info['name'], file_info['extension']), unsafe_allow_html=True)

def render_request_collab():
    st.markdown('---')
    if st.button('협업 요청하기'):
        st.session_state.collaboration_requested = not st.session_state.get('collaboration_requested', False)

    if st.session_state.get('collaboration_requested', False):  
        colab_uploaded_file = st.file_uploader("협업 요청 할 파일을 Drag&Drop으로 업로드 해주세요(:red[단일 파일]의 :red[.xlsx, .csv] 확장자만 지원됩니다.)", accept_multiple_files=False, type=['xlsx', 'csv'], key='uploader2')
        if colab_uploaded_file:
            file_info = files_processor.get_file_info(colab_uploaded_file)
            colab_formatted_columns = [f":red[**{{{col}}}**], " for col in file_info['columns']]
            colab_columns_str = ' '.join(colab_formatted_columns)
            st.markdown(f"추출된 컬럼을 활용하여 Prompt를 작성해주세요: {colab_columns_str}")
            colab_prompt = st.text_area("Prompt :red[*자동화 할 컬럼의 값은 중괄호 '{}' 로 표시해주세요(예시 참조)]", placeholder="Translate Korean to English:\nsrc: {src}\ntrg: {trg}", key='textarea1s')


            if 'colab_show_sample' not in st.session_state:
                st.session_state.colab_show_sample = False

            if 'colab_show_check_sample_btn' not in st.session_state:
                st.session_state.colab_show_check_sample_btn = False

            if st.button(' sample prompt') or st.session_state.colab_show_sample:
                if not colab_prompt:
                    st.error("Error: The prompt value is missing!")
                else:
                    st.session_state.colab_show_sample = True

                    colab_prompt = colab_prompt 
                    colab_matches = async_gpt.get_fstring_from_prompt(colab_prompt) 
                        
                    random_index = random.randint(0, file_info['dataframe'].shape[0] - 1)
                    for column_name in colab_matches:
                        if column_name in file_info['columns']:
                            value = file_info['dataframe'][column_name].iloc[random_index]
                            colab_prompt = colab_prompt.replace(f"{{{column_name}}}", f":red[{value}]")
                    
                    st.markdown(colab_prompt.replace('\n', '\n\n'))
                    st.session_state.show_check_sample_btn = True


                    colab_subject = st.text_input("Subject", placeholder="제목: (예: 한영 번역 자동화 요청 드립니다.)")
                    colab_name = st.text_input("Name", placeholder="작성자 이름: (예: 정경일)")
                    colab_department = st.text_input("Department", placeholder="작성자 소속: (예: 딥러닝연구팀)")
                    colab_content = st.text_area("Content", placeholder="협업 요청 내용: (예: tmp1.xlsx 파일의 src 컬럼을 gpt로 한글 번역하여 trg 컬럼에 삼입해주시면 감사드리겠습니다.)")

                    if st.button("Send Email"):
                        with st.spinner("The program is in progress. Please do not manipulate other elements while it's running...."):
                            if colab_subject and colab_name and colab_content:
                                email.send_email(colab_uploaded_file, colab_prompt, colab_subject, colab_name, colab_department, colab_content)
                                st.success("Email sent successfully!")
                                st.session_state.collaboration_requested = False
                            else:
                                st.error("Please fill in all required fields.")