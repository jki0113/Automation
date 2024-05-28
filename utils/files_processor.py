import base64
import pandas as pd
import io
import os

def get_file_info(uploaded_file):
    file_name = uploaded_file.name
    file_extension = os.path.splitext(file_name)[1]
    file_name_without_extension = os.path.splitext(file_name)[0]
    file_size = uploaded_file.size

    file_info = {
        "fullname": file_name,
        "name": file_name_without_extension,
        "extension": file_extension,
        "size": file_size
    }

    if file_extension in ['.xls', '.xlsx']:
        df = pd.read_excel(uploaded_file)
        columns = df.columns.tolist()
        file_info["columns"] = columns
        file_info["dataframe"] = df
        
    elif file_extension == '.csv':
        df = pd.read_csv(uploaded_file)
        columns = df.columns.tolist()
        file_info["columns"] = columns
        file_info["dataframe"] = df

    return file_info

def get_df_download_link(df, filename, extension):
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

    href = f'<a href="{mime};base64,{b64}" download="{filename}_result{extension}">다운로드</a>'
    return href

# difference comparsion처럼 pandas 대신 xlswriter를 사용하는 경우에는 BytesIO 객체를 받는 것 이기 때문에 아래의 방식으로 엑셀 다운로드 링크를 생성해야 함
def get_worksheet_download_link(output, filename="result.xlsx"):
    """find difference 워크시트 전용 다운로드 링크"""
    b64 = base64.b64encode(output.getvalue()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">다운로드</a>'
    return href