import streamlit as st

def home():
    st.markdown("""   """)
    st.title("DeepLearning - Automation Page")
    st.markdown("""---""")
    st.markdown("""
    ### 메뉴
    ##### - 엑셀 활용한 GPT 자동화
    ##### - 언어 감지 자동 추출
    ##### - 달라진 부분 비교
    ##### - 빈도수 기반 단어 카운트
    ##### - 엑셀 내 출현한 용어집 표시
    :red[*기능 별 상세 사용 방법은 맨 아래서 확인 가능합니다.]
    """)
    st.markdown("""---""")
    st.markdown("""### 상세 사용 방법""")
    buttons = [
        'GPT Excel Automation',
        "Language Extraction", 
        'Differences Comparsion', 
        'Word Count', 
        'Apply Vocab'
    ]

    selected_button = st.radio("상세 사용 방법 보기:", buttons, index=0)

    if selected_button == 'GPT Excel Automation':
        st.markdown("""---""")
        st.markdown("""
            ### GPT Excel Automation
        """)
        st.image("/home/lexcode/바탕화면/workspace/KyungillJung/230911-automation_v2/assets/img/how2use_gpt_excel_automation_1.png", use_column_width=True)
        st.markdown("""step 01. GPT를 자동화하고자 하는 파일을 업로드합니다.""")
        st.markdown("""---""")
        st.image("/home/lexcode/바탕화면/workspace/KyungillJung/230911-automation_v2/assets/img/how2use_gpt_excel_automation_2.png", use_column_width=True)
        st.markdown("""step 02-1. 추출된 컬럼을 기반으로 프롬프트를 작성합니다. (이때 프롬프트에 자동화되어 들어갈 컬럼은 중괄호{}로 감싸져 있어야 합니다.)""")
        st.markdown("""step 02-2. 프롬프트를 작성하고 'sample prompt' 버튼을 눌러 실제 프롬프트가 어떻게 적용되는지 확인합니다.""")
        st.markdown("""step 02-3. 'run automation' 버튼을 눌러 자동화를 실행합니다. ('processing request' 문구를 통해 몇 번째 row가 GPT에 입력되는지 확인할 수 있으며 한 요청에서 최대 10분까지 시간이 소요될 수 있습니다.)""")
        st.markdown("""step 02-4. 자동화가 완료되면 '다운로드 링크' 버튼을 눌러 자동화 완료된 파일을 다운로드합니다.""")
        st.markdown("""---""")
        st.image("/home/lexcode/바탕화면/workspace/KyungillJung/230911-automation_v2/assets/img/how2use_gpt_excel_automation_3.png", use_column_width=True)
        st.markdown("""step 03-1. [이메일로 협업 요청하기] 자동화 협업을 요청하고자 하는 파일을 업로드합니다.""")
        st.markdown("""step 03-2. [이메일로 협업 요청하기] 사용할 수 있는 컬럼을 기반으로 준비한 프롬프트를 작성합니다.""")
        st.markdown("""step 03-3. [이메일로 협업 요청하기] 프롬프트를 작성하고 'sample prompt' 버튼을 눌러 실제 프롬프트가 어떻게 적용되는지 확인합니다.""")
        st.markdown("""step 03-4. [이메일로 협업 요청하기] 협업 요청할 이메일 제목, 이름, 부서, 상세 내용을 작성하고 'send email' 버튼을 클릭하여 협업 요청 이메일을 전송합니다.""")

    elif selected_button == "Language Extraction":
        st.markdown("""---""")
        st.markdown("### Language Extraction")
        st.image("/home/lexcode/바탕화면/workspace/KyungillJung/230911-automation_v2/assets/img/how2use_language_extraction_1.png", use_column_width=True)
        st.markdown("""step 01. 언어 추출을 자동화하고자 하는 파일을 업로드합니다.""")
        st.markdown("""---""")
        st.image("/home/lexcode/바탕화면/workspace/KyungillJung/230911-automation_v2/assets/img/how2use_language_extraction_2.png", use_column_width=True)
        st.markdown("""step 02-1. 추출하고자 하는 컬럼을 선택합니다.""")
        st.markdown("""step 02-2. Threshold를 선택합니다. 40으로 설정할 경우 40% 이상의 확률로 예측된 경우만 추출하고 40% 미만의 확률로 예측된 경우 UNK를 표시합니다.""")
        st.markdown("""step 02-3. 'extract' 버튼을 누르고 자동화가 완료될 때까지 기다립니다.""")
        st.markdown("""step 02-4. 자동화가 끝나면 다운로드 링크를 클릭하여 결과를 다운로드합니다.""")

    elif selected_button == 'Differences Comparsion':
        st.markdown("""---""")
        st.markdown("### Differences Comparison")
        st.image("/home/lexcode/바탕화면/workspace/KyungillJung/230911-automation_v2/assets/img/how2use_difference_comparsion_1.png", use_column_width=True)
        st.markdown("""step 01. 다른 부분을 비교하고자 하는 파일을 업로드합니다.""")
        st.markdown("""---""")
        st.image("/home/lexcode/바탕화면/workspace/KyungillJung/230911-automation_v2/assets/img/how2use_difference_comparsion_2.png", use_column_width=True)
        st.markdown("""step 02-1. 비교하고자 하는 두 컬럼을 선택합니다.""")
        st.markdown("""step 02-2. 'compare' 버튼을 눌러 자동화를 실행합니다.""")
        st.markdown("""step 02-3. 자동화가 끝나면 다운로드 링크를 클릭하여 결과를 다운로드합니다.""")

    elif selected_button == 'Word Count':
        st.markdown("""---""")
        st.markdown("### Word Count")
        st.image("/home/lexcode/바탕화면/workspace/KyungillJung/230911-automation_v2/assets/img/how2use_wordcount_1.png", use_column_width=True)
        st.markdown("""step 01. 빈도수를 추출하고자 하는 파일을 업로드합니다.""")
        st.markdown("""---""")
        st.image("/home/lexcode/바탕화면/workspace/KyungillJung/230911-automation_v2/assets/img/how2use_wordcount_2.png", use_column_width=True)
        st.markdown("""step 02-1. 'Extract' 버튼을 눌러 자동화를 실행합니다.""")
        st.markdown("""step 02-2. 자동화가 끝나면 다운로드 링크를 클릭하여 결과를 다운로드합니다.""")


    elif selected_button == 'Apply Vocab':
        st.markdown("""---""")
        st.markdown("### Apply Vocab")
        st.image("/home/lexcode/바탕화면/workspace/KyungillJung/230911-automation_v2/assets/img/how2use_apply_vocab_1.png", use_column_width=True)
        st.markdown("""step 01. 용어집을 적용할 문장이 있는 파일을 업로드합니다.""")
        st.markdown("""---""")
        st.image("/home/lexcode/바탕화면/workspace/KyungillJung/230911-automation_v2/assets/img/how2use_apply_vocab_2.png", use_column_width=True)
        st.markdown("""step 02. 업로드한 파일에서 용어집을 적용할 컬럼을 선택합니다.""")
        st.markdown("""---""")
        st.image("/home/lexcode/바탕화면/workspace/KyungillJung/230911-automation_v2/assets/img/how2use_apply_vocab_3.png", use_column_width=True)
        st.markdown("""step 03. 용어집을 적용할 용어가 있는 파일을 업로드합니다. (출발어, 도착어 최소 두 개의 컬럼이 필요합니다.)""")
        st.markdown("""---""")
        st.image("/home/lexcode/바탕화면/workspace/KyungillJung/230911-automation_v2/assets/img/how2use_apply_vocab_4.png", use_column_width=True)
        st.markdown("""step 04-1. 적용할 용어집의 원문과 번역문을 선택합니다.""")
        st.markdown("""step 04-2. 'Apply Vocab' 버튼을 눌러 자동화를 실행합니다.""")
        st.markdown("""step 04-3. 자동화가 끝나면 다운로드 링크를 클릭하여 결과를 다운로드합니다.""")
    st.markdown("""---""")
    st.markdown("""
    ### 주의사항
     - 단일 파일에 대한 자동화만 지원하고 있습니다.  
     - 웹페이지에 지연이 발생할 수 있습니다.  
     - 자동화 실행 중 다른 요소를 조작하지 말아주세요.  
     - 프로그램 실행 중 에러가 발생할 경우 에러 화면과 에러 파일을 캡처해서 팀즈 보내주시면 빠르게 조치하겠습니다.  
    """)
    st.markdown("""---""")
    # st.markdown("""
    # ### 버전 업데이트 정보
    # :blue[230911]  
    # init  
    # :blue[230917]  
    # 사용성 개선 문구 추가  
    # GPT Excel Automation - sample prompt에 markdown 문법 들어가 있을 경우 화면에서 제대로 나올 수 있도록 후처리  
    # GPT Excel Automation - sample prompt 버튼 클릭 하지 않으면 다음 단계로 넘어가지 않도록 수정  
    # """)
    # st.markdown("""---""")


    # st.markdown("""---""")
    # st.markdown("*Streamlit* is **really** ***cool***.")
    # st.markdown('''
    #     :red[Streamlit] :orange[can] :green[write] :blue[text] :violet[in]
    #     :gray[pretty] :rainbow[colors].''')
    # st.markdown("Here's a bouquet &mdash;\
    #             :tulip::cherry_blossom::rose::hibiscus::sunflower::blossom:")

    # multi = '''If you end a line with two spaces,
    # a soft return is used for the next line.

    # Two (or more) newline characters in a row will result in a hard return.
    # '''
    # st.markdown(multi)
