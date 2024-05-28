import textract
import tempfile
import pandas as pd

def extract_and_split_text_from_docx(uploaded_file):
    """파일로부터 텍스트를 추출하고 문단 기준으로 분리된 리스트를 반환"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
        temp_file.write(uploaded_file.getvalue())
        temp_file_path = temp_file.name
    text = textract.process(temp_file_path).decode('utf-8-sig')
    return [line.strip() for line in text.split('\n\n') if line.strip()]

def convert_two_column_excel_from_lists(para_list):
    """추출한 텍스트 리스트를 홀수번째와 짝수번째로 나누어 데이터프레임 생성"""
    src = para_list[::2]
    trg = para_list[1::2]
    
    max_length = max(len(src), len(trg))
    src += [''] * (max_length - len(src))
    trg += [''] * (max_length - len(trg))
    
    df = pd.DataFrame({'SRC': src, 'TRG': trg})
    return df
