### 담당자
- 석슬기

### 개요
딥러닝 연구팀 자동화 업무 요청 시 자주 요청하는 PM도 매번 작업하는 저도 불편함이 있어서 만든 자동화 페이지 입니다. 6층 딥러닝 연구팀 서버에 배포하였으며 streamlit 기반으로 프론트를 제작하였습니다. 자동화는 개발자 개개인이 가장 편하고 쉬운 방법으로 작업하는게 제일 효율적이라고 판단하여 현재 진행중인 세계법제처 이외에는 유지보수 계획은 없습니다.

### 필요기술
- gpt 비동기 처리
- streamlit
- 각종 요청사항에 요구되는 기술
### 환경
- 서버: 6층 딥러닝 연구팀 서버
- 가상환경: jki_automation
- 포트: 8888:8888
- 위치: /home/lexcode/바탕화면/workspace/KyungillJung/230911-automation_v2
- 깃허브 주소: https://github.com/LexcodeHQ/automation
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