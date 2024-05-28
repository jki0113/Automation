import pandas as pd
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell
import difflib
import io
import streamlit as st
from tqdm import tqdm
from stqdm import stqdm

def levenshtein_distance(text_a, text_b):
    matcher = difflib.SequenceMatcher(None, text_a, text_b)
    distance = 1 - matcher.ratio()
    return distance * 100

def navigation_formation(text_list_a, text_list_b):
    result_a = []
    result_b = []
    for text_a , text_b in stqdm(zip(text_list_a, text_list_b), total=len(text_list_a), desc="Identifying the differences."):
        diff = list(difflib.ndiff(text_a, text_b))

        tmp_result_a = []
        tmp_result_b = []

        idx_a = 0
        idx_b = 0

        for item in diff:
            if item.startswith('-'):
                tmp_result_a.append({item[2:] : 'red'})
                idx_a += 1
            elif item.startswith('+'):
                tmp_result_b.append({item[2:] : 'red'})
                idx_b += 1
            else:
                tmp_result_a.append({item[2:] : 'default'})
                tmp_result_b.append({item[2:] : 'default'})
                idx_a += 1
                idx_b += 1

        result_a.append(tmp_result_a)
        result_b.append(tmp_result_b)
    return [result_a, result_b]


def find_diff(file, extension, column_1, column_2):
    print('find_diff - read file', end='')
    data = pd.read_excel(file) if extension == '.xlsx' else pd.read_csv(file, encoding='utf-8-sig')
    print(' -> done')
    data.fillna('', inplace=True)
    data = data.astype(str)

    text_list_a = data[column_1].tolist()
    text_list_b = data[column_2].tolist()

    print('find_diff - find difference', end='')
    result_a, result_b = navigation_formation(text_list_a, text_list_b)
    print(' -> done')

    data = []
    for a, b in zip(result_a, result_b):
        tmp = [a, b]
        data.append(tmp)

    ratio_list = []
    for a, b in stqdm(zip(text_list_a, text_list_b), total=len(text_list_a), desc="Using the Levenshtein distance to calculate the ratio of differences."):
        ratio_list.append(levenshtein_distance(a, b))

    print('find_diff - make file', end='')
    output = io.BytesIO()
    write_workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    write_workbook.use_zip64()
    worksheet = write_workbook.add_worksheet()

    red_format = write_workbook.add_format({'font_color': 'red'})
    default_format = write_workbook.add_format({'font_color': 'black'})

    # A, B 컬럼 삽입
    worksheet.write(0, 0, f'{column_1}')
    worksheet.write(0, 1, f'{column_2}')

    # Streamlit progress bar 초기화
    # progress_bar = st.progress(0)
    # status_text = st.empty()

    for row, (lines, ratio) in enumerate(stqdm(zip(data, ratio_list), total=len(data), desc="Writing a new Excel file.")):
        # Streamlit progress bar 업데이트
        # progress_bar.progress((row + 1) / len(data))
        # status_text.text(f"Progress: {((row + 1) / len(data)) * 100}%")
        for col, line in enumerate(lines):
            if not line:
                worksheet.write(row + 1, col, "")
            else:
                rich_text = []
                for char_dict in line:
                    char, color = list(char_dict.items())[0]
                    if color == 'red':
                        rich_text.extend([red_format, char])
                    else:
                        rich_text.extend([default_format, char])
                cell = xl_rowcol_to_cell(row + 1, col)
                worksheet.write_rich_string(cell, *rich_text)
        
        # ratio 컬럼 삽입
        worksheet.write(row + 1, 2, ratio)

    write_workbook.close()
    output.seek(0)
    print(' -> done')
    return output
