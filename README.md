### 개요
- 내부 직원이 활용하는 자연어 처리 및 다양한 작업들의 자동화 페이지입니다.
- streamlit으로 배포하였으며 pm2로 관리합니다.
- 각 메뉴들에 대한 설명은 아래와 같습니다
    - Prompt Test: 각종 LLM을 테스트 할 수 있는 프롬프트 테스트
    - GPT Excel Automation: GPT를 엑셀 각 row에 일괄 적용
    - Language Extraction: 엑셀 전체 row에 언어를 추출
    - Differences Comparsions: 엑셀에서 두개의 컬럼의 변경률과 변경된 부분 색 표시
    - Word Count: 파일 내의 용어집 빈도 수 추출
    - Apply Vocab: 문장에 적용되어야 할 용어집 추출
    - ACC Automation: 아시아문화전당 전용 메뉴
    - HSA: 번역 결과물 검토 자동화 (선아 씨)
    - LKH: 세계 법제처 조문 체계 자동화
### 구성
```
/home/lexcode/바탕화면/workspace/KyungillJung/230911-automation_v2
├── README.md
├── assets # 페이지 렌더링에 필요한 이미지, 안내 문구 등 구성 요소
│   ├── display.py
│   └── img
├── automation.py # 전체 앱을 실행해주는 main.py 
├── menu # 각 기능 별 페이지를 렌더링하기 위해 필요한 폴더
│   ├── LKH.py # 세계법제 전용 자동화 페이지
│   ├── acc.py # 아시아문화전당 전용 자동화 페이지   
│   ├── apply_vocab.py # 용어집 표시 자동화 페이지
│   ├── differences_comparsion.py # 서로다른 부분 표시 및 변경률 표시 자동화 페이지
│   ├── gpt_excel_automation.py # gpt 엑셀 자동화 페이지
│   ├── hsa.py # 선아 씨 요청사항 자동화 페이지
│   ├── language_extraction.py # 언어 감지 및 추출 자동화 페이지
│   ├── prompt_test.py # 프롬프트 모델 테스트 자동화 페이지
│   └── word_count.py # 문서 내 단어 빈도수 추출 자동화 페이지
├── requirements.txt
├── run_automation.py # pm2 매니징을 위한 서브프로세서(이 py 파일을 실행해서 앱을 실행합니다)
└── utils # 각 메뉴에 있는 자동화를 실행하기 위한 기능 폴더
    ├── acc_fun.py
    ├── apply_vocab.py
    ├── async_gpt.py
    ├── differences_comparsion.py
    ├── docx_processor.py
    ├── email.py
    ├── files_processor.py
    ├── hsa.py
    ├── language_extraction.py
    ├── legislative_automation.py
    ├── numeric_comparsion.py
    ├── prompt_test.py
    └── word_count.py
```

### 실행방법
- streamlit으로 앱을 실행할 때 python ~.py 로 실행하는 것이 아닌 streamlit run ~.py 방식으로 실행되며 앱 자체를 pm2 로 관리하기 때문에 subprocessor를 통해 실행 됨
- 실행하는 방법은 아래와 같음
    
    `cd /home/lexcode/바탕화면/workspace/KyungillJung/230911-automation_v2`
    
    `conda activate jki_automation`
    
    `pip install -r requirement.txt`
    
    `pm2 start run_automation.py --name automation_v2 --interpreter python --log-date-format "YYYY-MM-DD HH:mm:ss"`