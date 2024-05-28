import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import streamlit as st
import mimetypes  # 추가된 부분
import os

def send_email(uploaded_file, prompt, subject, name, department, content):
    email_list = [
        # 'kijung@lexcode.com',
        'nlp@lexcode.com'
    ]

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")  
    from_email = os.getenv("SMTP_FROM_EMAIL")

    body = f'''
Name: {name}
Department: {department}
Content:
{content}
Prompt:
{prompt}
    '''

    for to_email in email_list:
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

    mime_type, encoding = mimetypes.guess_type(uploaded_file.name)
    if mime_type is None:
        mime_type = 'application/octet-stream'
    main_type, sub_type = mime_type.split('/', 1)
    part = MIMEBase(main_type, sub_type)

    file_content = uploaded_file.getvalue()
    part.set_payload(file_content)
    encoders.encode_base64(part)

    part.add_header('Content-Disposition', 'attachment', filename=uploaded_file.name)
    msg.attach(part)

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)