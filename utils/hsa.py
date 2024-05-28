import io
import textract
import pandas as pd
import tempfile
from utils.async_gpt import *
import base64
import re

def extract_text_from_file(uploaded_file):
    """파일로부터 텍스트를 추출하고 문단 기준으로 분리된 리스트를 반환"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
        temp_file.write(uploaded_file.getvalue())
        temp_file_path = temp_file.name
    text = textract.process(temp_file_path).decode('utf-8-sig')
    return [line.strip() for line in text.split('\n\n') if line.strip()]

def process_document_alignment(src, trg):
    """SRC와 TRG 리스트를 받아 양단편집을 위한 데이터프레임을 생성"""
    length_difference = abs(len(src) - len(trg))

    if len(src) < len(trg):
        src.extend([''] * length_difference)
    elif len(trg) < len(src):
        trg.extend([''] * length_difference)

    return pd.DataFrame({'source': src, 'target': trg})


def process_vocab_detection(aligned_df, vocab_df):
    """양단편집 df와 용어집df를 입력"""
    # 용어찾기 수행
    aligned_df['detected'] = aligned_df['source'].apply(lambda x: ', '.join(find_voacb_in_df(x, vocab_df)))
    # gpt로 타겟컬럼에서 찾기 수행
    aligned_df, combined_result_df = find_voacb_in_trg(aligned_df)
    # 용어집으로 따로 추출한 용어는 한번 정제해야함 240306 윤국 씨 기준
    combined_result_df = process_combined_result_df(combined_result_df)
    # 색칠공부
    return aligned_df, combined_result_df

def remove_parentheses(text):
    """괄호와 괄호 안의 내용을 제거합니다."""
    return re.sub(r'\(.*?\)', '', text).strip()

def process_combined_result_df(df):
    # 대소문자 구분 없이 source와 target이 완전히 같은 행 제거
    df['source_lower'] = df['source'].str.lower()
    df['target_lower'] = df['target'].str.lower()
    df = df.drop_duplicates(subset=['source_lower', 'target_lower'])

    # 대소문자 구분 없이 source와 target이 서로 같은 행 제거
    df = df[df['source_lower'] != df['target_lower']]
    
#####################################################################################################
    # 괄호를 포함하는 target 식별
    df['has_parenthesis'] = df['target'].apply(lambda x: '(' in x and ')' in x)
    # 괄호 제거된 target 버전 생성
    df['target_no_parentheses'] = df['target'].apply(remove_parentheses)

    # 괄호 있는 버전과 없는 버전이 동일한 경우, 괄호 없는 버전 제거
    df_duplicated_with_parentheses = df[df.duplicated(['source_lower', 'target_no_parentheses'], keep=False) & df['has_parenthesis']]
    df_unique = df.drop_duplicates(['source_lower', 'target_no_parentheses'], keep=False)
    df_combined = pd.concat([df_duplicated_with_parentheses, df_unique]).drop_duplicates(['source', 'target'], keep='first')
#####################################################################################################

    # 대소문자 구분 없이 source를 기준으로 target을 합침
    df_final = df_combined.groupby('source_lower').agg({
        'source': 'first',  # 소문자화된 source 기준으로 첫 번째 나타나는 원본 source 사용
        'target': lambda x: ', '.join(sorted(set(x)))  # 동일 source에 대한 target은 합침
    }).reset_index(drop=True)

    return df_final.drop(columns=['source_lower', 'target_lower', 'has_parenthesis', 'target_no_parentheses'], errors='ignore')

def find_voacb_in_df(aligned_df, vocab_df):
    # 여기에서는 용어 찾기 수행
    detected_words = []
    for index, row in vocab_df.iterrows():
        if row['source'] in aligned_df:
            detected_words.append(row['source'])
    return detected_words

def find_voacb_in_trg_prompt(src,trg,detected):
    # gpt로 타겟 컬럼에서 찾기 수행해주는 프롬프트 작성
    prompt = f"""You have been tasked with performing a specific operation on the given data. The data we are dealing with includes a dataframe with the following columns: SRC, TRG, and DETECTED. Here, the SRC column contains sentences written in English, the TRG column contains those English sentences translated into Korean, and the DETECTED column contains specific English words extracted from the sentences in the SRC column.

Your task is as follows:

- Find the English words listed in the DETECTED column in each sentence of the SRC column.
- Determine how each found English word is translated in the Korean sentences in the TRG column.
- Use this information to create a new JSON-formatted result that represents the Korean translation for each DETECTED word. The result should be stored under the key "result" as a dictionary, with each key being the English word from the DETECTED column and its value being a list of Korean terms that represent how the word is translated in the TRG column. Every translation, even if there is only one, should be included in a list.

```SRC: {src}
```TRG: {trg}
```DETECTED: {detected}
```result: 
"""
    return prompt

def process_gpt_result(gpt_result):
    processed_result_str = ""
    df_rows = []
    
    for key, values in gpt_result.items():
        # 리스트 값들을 콤마로 구분된 문자열로 합치기
        values_str = ", ".join(values)
        processed_result_str += f"{key}: {values_str}\n"
        
        # 데이터프레임 행 추가를 위해 (키, 값) 쌍을 리스트에 추가
        for value in values:
            df_rows.append((key, value))
    
    # 문자열 마지막의 개행문자 제거
    processed_result_str = processed_result_str.strip()
    
    # 데이터프레임 생성
    result_df = pd.DataFrame(df_rows, columns=['source', 'target'])
    
    return processed_result_str, result_df

def find_voacb_in_trg(aligned_df):
    aligned_df['result'] = ''
    aligned_df['price'] = .0
    all_result_dfs = []  # 결과 데이터프레임들을 저장할 리스트

    prompt_list = [
        find_voacb_in_trg_prompt(aligned_df['source'][idx], aligned_df['target'][idx], aligned_df['detected'][idx])
        for idx in range(aligned_df.shape[0])
        if pd.notnull(aligned_df['detected'][idx]) and aligned_df['detected'][idx] != ''
    ]
    valid_indexes = [idx for idx in range(aligned_df.shape[0]) if pd.notnull(aligned_df.loc[idx, 'detected']) and aligned_df.loc[idx, 'detected'] != '']
    
    MODEL = 'gpt-4-0125-preview'
    async_gpt_result = asyncio.run(
        process_api_requests_from_prompt_list(
            prompt_list=prompt_list,
            model=MODEL,
            temperature=.0,
            api_key=OPENAI_KEY,
            request_url="https://api.openai.com/v1/chat/completions",
            json_mode=True,
            timeout=50,
            desc="find vocab in trg"
        )
    )
    
    for i, gpt_result in enumerate(async_gpt_result):
        if gpt_result is None:
            continue
        idx = valid_indexes[i]
        raw_result = gpt_result[1][1]['choices'][0]['message']['content']
        parsed_result_str, result_df = process_gpt_result(parse_json_string(raw_result, ['result'])['result'])

        aligned_df.at[idx, 'result'] = parsed_result_str
        all_result_dfs.append(result_df)  # 각 결과를 all_result_dfs 리스트에 추가

        if MODEL == 'gpt-3.5-turbo-0125':
            aligned_df.at[idx, 'price'] = (gpt_result[1][1]['usage']['prompt_tokens'] * 0.0005 / 1000) + (gpt_result[1][1]['usage']['completion_tokens'] * 0.0015 / 1000)
        elif MODEL == 'gpt-4-0125-preview':
            aligned_df.at[idx, 'price'] = (gpt_result[1][1]['usage']['prompt_tokens'] * 0.01 / 1000) + (gpt_result[1][1]['usage']['completion_tokens'] * 0.03 / 1000)
    
    # for 루프가 완료된 후 모든 결과 데이터프레임들을 하나로 합치기
    combined_result_df = pd.concat(all_result_dfs, ignore_index=True)
    combined_result_df.to_excel('/home/lexcode/바탕화면/workspace/KyungillJung/230911-automation_v2/tmp/tmp.xlsx')
    return aligned_df, combined_result_df

def rewrite_in_richtext(result_df):
    # 임시 파일 생성
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
    temp_file_path = temp_file.name
    temp_file.close()  # 파일을 닫고, 경로를 사용해 작업 진행

    writer = pd.ExcelWriter(temp_file_path, engine='xlsxwriter')
    workbook = writer.book
    worksheet = workbook.add_worksheet('Sheet1')
    

    red_format = workbook.add_format({'font_color': 'red'})
    black_format = workbook.add_format({'font_color': 'black'})

    # 데이터프레임의 컬럼명을 엑셀 파일에 쓰기
    for col_num, value in enumerate(result_df.columns.values):
        worksheet.write(0, col_num, value, black_format)

    # 데이터프레임 순회
    for row_idx, row in result_df.iterrows():
        detected_words = str(row['detected']).split(', ')
        source_text = str(row['source'])
        
        # detected 용어에 대해 리치 텍스트로 처리된 문자열 생성
        # 먼저 전체 텍스트를 검은색 텍스트로 추가
        rich_text_list = [black_format, source_text]
        
        # detected 용어를 빨간색으로 표시
        for word in detected_words:
            if word in source_text:
                start_idx = source_text.find(word)
                end_idx = start_idx + len(word)
                
                # 단어가 있는 부분을 빨간색으로 변경
                rich_text_list.append(source_text[:start_idx])
                rich_text_list.append(red_format)
                rich_text_list.append(source_text[start_idx:end_idx])
                rich_text_list.append(black_format)
                rich_text_list.append(source_text[end_idx:])
        
        # 리치 텍스트를 셀에 적용
        worksheet.write_rich_string(row_idx + 1, 0, *rich_text_list)
        
        # 나머지 컬럼 값 쓰기 (이 예시에서는 'source' 컬럼만 처리합니다)
        # 다른 컬럼도 필요에 따라 비슷하게 처리 가능

    workbook.close()
    return temp_file_path

def get_download_link(df, filename, extension, href):
    if extension == ".csv":
        data = df.to_csv(index=False, encoding="utf-8-sig")
        mime = "data:file/csv"
        b64 = base64.b64encode(data.encode('utf-8-sig')).decode()
    elif extension == ".xlsx":
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        mime = "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        data = output.getvalue()
        b64 = base64.b64encode(data).decode()
    else:
        raise ValueError(f"Unsupported file extension: {extension}")

    href = f'<a href="{mime};base64,{b64}" download="{filename}_result{extension}">{href}</a>'
    # print('@' * 100)
    # print(href)
    # print('@' * 100)
    return href