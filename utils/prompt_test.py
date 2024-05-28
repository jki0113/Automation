
import streamlit as st
from openai import OpenAI
import anthropic
import os

# API 클라이언트 초기화
openai_client = OpenAI(api_key=os.getenv("OPENAI_GPT_API_KEY"))
claude_client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_GPT_API_KEY"))

def generate_response_gpt(model, temperature, message):
    response = openai_client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "user", "content": message}
        ],
        stream=True,
    )
    for chunk in response:
        chunk_message = chunk.choices[0].delta
        if hasattr(chunk_message, 'content'):
            content = chunk_message.content
            yield content

def generate_response_claude(model, temperature, message, max_tokens=1024):
    with claude_client.messages.stream(
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": message}],
        model=model,
        temperature=temperature,
    ) as stream:
        for text in stream.text_stream:
            yield text
