import re
import pandas as pd
import xlsxwriter
from io import BytesIO 

def extract_numbers(text):
    text = str(text)
    numbers = re.findall(r'\d+', text)
    return numbers

def check_translation_numbers(src, trg):
    src_numbers = extract_numbers(src)
    trg_numbers = extract_numbers(trg)
    
    # SRC에서 나타난 각 숫자를 TRG에서의 빈도와 비교하여 누락된 횟수를 계산
    missing_in_trg = []
    for num in src_numbers:
        if src_numbers.count(num) > trg_numbers.count(num):
            # SRC에 있는 횟수가 TRG에 있는 횟수보다 많은 경우, 누락된 것으로 간주
            missing_in_trg.append(num)
            # 이미 체크한 숫자는 TRG 리스트에서 제거하여 중복 계산을 방지
            trg_numbers = [n for n in trg_numbers if n != num]

    if missing_in_trg:
        # 누락된 숫자들을 문자열로 변환하여 반환
        missing_items = ', '.join(missing_in_trg)
        return f'{missing_items}'
    else:
        return ''
    
def apply_number_style_formatter(df, target_columns):
    """입력 받은 데이터 프레임과 해당 데이터 프레임의 target_columns를 빨간색으로 색칠"""
    df.fillna(' ', inplace=True)
    df = df.astype(str)
    
    # 메모리 상에서 엑셀 파일 생성
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1', header=False, startrow=1)
    
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    
    # 서식 객체 생성
    red_format = workbook.add_format({'font_color': 'red'})
    black_format = workbook.add_format({'font_color': 'black'})
    
    # 컬럼 헤더 작성
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value)
    
    # 데이터프레임을 순회하면서 서식 적용
    for col_idx, col_name in enumerate(df.columns):
        if col_name in target_columns:  # 해당 컬럼만 처리
            for row_idx, value in enumerate(df[col_name]):
                # 각 셀의 문자를 검사하여 서식을 적용할 문자열 생성
                rich_text_list = []
                str_value = str(value)
                if str_value:  # 값이 있는 경우에만 처리
                    for char in str_value:
                        if re.match(r'\d', char):  # 문자가 숫자인 경우
                            rich_text_list.append(red_format)
                            rich_text_list.append(char)
                        else:  # 문자가 숫자가 아닌 경우
                            rich_text_list.append(black_format)
                            rich_text_list.append(char)
                    
                    # rich_text_list가 비어있지 않은 경우에만 셀에 작성
                    if rich_text_list:
                        worksheet.write_rich_string(row_idx + 1, col_idx, *rich_text_list)
                    else:
                        worksheet.write(row_idx + 1, col_idx, str_value)
                else:  # 값이 없는 경우
                    worksheet.write(row_idx + 1, col_idx, '')
        else:  # 해당 컬럼이 아닌 경우 그대로 값 쓰기
            for row_idx, value in enumerate(df[col_name]):
                worksheet.write(row_idx + 1, col_idx, str(value))
    
    # 파일 저장 및 닫기
    writer.close()
    
    # BytesIO 객체를 반환
    output.seek(0)
    return output