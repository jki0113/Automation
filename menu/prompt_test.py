import streamlit as st
from openai import OpenAI
import functools
import anthropic
import os
from concurrent.futures import ThreadPoolExecutor
import asyncio
import nest_asyncio
from queue import Queue
import concurrent.futures
import time

openai_client = OpenAI(api_key=os.getenv("OPENAI_GPT_API_KEY"))
claude_client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_GPT_API_KEY"))

# OpenAI GPT 응답 생성 함수
def generate_response_openai(model, temperature, message):
    response = openai_client.chat.completions.create(
        max_tokens=2048,
        model=model,
        temperature=temperature,
        messages=[
            {"role": "user", "content": message}
        ],
        stream=True,
    )
    for chunk in response:
        chunk_message = chunk.choices[0].delta
        content = chunk_message.content
        if content is not None:
            yield content

# Claude 응답 생성 함수
def generate_response_claude(model, temperature, message):
    with claude_client.messages.stream(
        max_tokens=2048,
        messages=[{"role": "user", "content": message}],
        model=model,
        temperature=temperature,
    ) as stream:
        for text in stream.text_stream:
            yield text

def collect_response(model, prompt):
    if "gpt" in model:
        response_generator = generate_response_openai(model, 0, prompt)
    else:
        response_generator = generate_response_claude(model, 0, prompt)
    
    # 제너레이터의 모든 내용을 문자열로 합쳐서 반환
    response = "".join(list(response_generator))
    return model, response
    
def render_prompt_test():
    st.title("Prompt Test")

    # 모델 선택 체크박스
    models = [
        "claude-3-haiku-20240307",
        "claude-3-sonnet-20240229",
        "claude-3-opus-20240229",
        "gpt-3.5-turbo-0125",
        "gpt-4-0125-preview",
        "gpt-4"
    ]
    selected_models = st.multiselect("Select models (at least one)", models, models)

    prompt = st.text_area("Enter your prompt", placeholder="Please enter your prompt")

    if st.button("Run"):
        if prompt.strip() == "":
            st.error("Please enter a prompt")
        elif len(selected_models) == 0:
            st.error("Please select at least one model")
        else:
            with st.spinner("Generating responses..."):
                start_time = time.time()

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future_to_model = [executor.submit(collect_response, model, prompt) for model in selected_models]
                    results = [future.result() for future in concurrent.futures.as_completed(future_to_model)]

                execution_time = time.time() - start_time
                st.write(f"Execution time: {execution_time:.2f} seconds")
                # 결과 출력
                for model, response in sorted(results, key=lambda x: selected_models.index(x[0])):
                    st.markdown(f"##### :red[{model}]")
                    st.markdown(f"{response}")
                    # st.markdown(f"<pre>{response}</pre>", unsafe_allow_html=True)
                    # st.markdown(f"```\n{response}\n```")
                    st.markdown('---')

            # 실행 시간 출력

# def render_page():
#     st.title("Prompt Test")
#     message = st.text_area("프롬프트를 입력하세요")
#     if st.button("실행"):
#         asyncio.set_event_loop(asyncio.new_event_loop())
#         loop = asyncio.get_event_loop()
#         nest_asyncio.apply(loop)
        
#         queues = [Queue() for _ in range(6)]
        
#         async def process_model(func, queue):
#             async for text in func(message):
#                 queue.put(text)
#             queue.put(None)
        
#         with ThreadPoolExecutor(max_workers=6) as executor:
#             futures = [
#                 loop.run_in_executor(executor, functools.partial(asyncio.run, process_model(func, queue)))
#                 for func, queue in zip(
#                     [
#                         generate_haiku,
#                         generate_sonnet,
#                         generate_opus,
#                         generate_35turbo,
#                         generate_4turbo,
#                         generate_4,
#                     ],
#                     queues,
#                 )
#             ]
#             loop.run_until_complete(asyncio.gather(*futures))
            
#         col1, col2, col3 = st.columns(3)
#         with col1:
#             st.subheader("Haiku")
#             output = ""
#             while True:
#                 text = queues[0].get()
#                 if text is None:
#                     break
#                 output += text
#             st.markdown(output)
            
#             st.subheader("Sonnet")
#             output = ""
#             while True:
#                 text = queues[1].get()
#                 if text is None:
#                     break
#                 output += text
#             st.markdown(output)
            
#         with col2:
#             st.subheader("Opus")
#             output = ""
#             while True:
#                 text = queues[2].get()
#                 if text is None:
#                     break
#                 output += text
#             st.markdown(output)
            
#             st.subheader("GPT-3.5-Turbo")
#             output = ""
#             while True:
#                 text = queues[3].get()
#                 if text is None:
#                     break
#                 output += text
#             st.markdown(output)
            
#         with col3:
#             st.subheader("GPT-4-Turbo")
#             output = ""
#             while True:
#                 text = queues[4].get()
#                 if text is None:
#                     break
#                 output += text
#             st.markdown(output)
            
#             st.subheader("GPT-4")
#             output = ""
#             while True:
#                 text = queues[5].get()
#                 if text is None:
#                     break
#                 output += text
#             st.markdown(output)

# async def generate_haiku(message):
#     with claude_client.messages.stream(
#         max_tokens=2048,
#         messages=[{"role": "user", "content": message}],
#         model="claude-3-haiku-20240307",
#     ) as stream:
#         for text in stream.text_stream:
#             yield f"{text}"

# async def generate_sonnet(message):
#     with claude_client.messages.stream(
#         max_tokens=2048,
#         messages=[{"role": "user", "content": message}],
#         model="claude-3-sonnet-20240229",
#     ) as stream:
#         for text in stream.text_stream:
#             yield f"{text}"

# async def generate_opus(message):
#     with claude_client.messages.stream(
#         max_tokens=2048,
#         messages=[{"role": "user", "content": message}],
#         model="claude-3-opus-20240229",
#     ) as stream:
#         for text in stream.text_stream:
#             yield f"{text}"

# async def generate_35turbo(message):
#     response = openai_client.chat.completions.create(
#         model="gpt-3.5-turbo-0125",
#         temperature=0,
#         messages=[{"role": "user", "content": message}],
#         stream=True,
#     )
#     for chunk in response:
#         if chunk.choices[0].delta is not None:
#             chunk_message = chunk.choices[0].delta
#             text = chunk_message.content
#             yield f"{text}"

# async def generate_4turbo(message):
#     response = openai_client.chat.completions.create(
#         model="gpt-4-0125-preview",
#         temperature=0,
#         messages=[{"role": "user", "content": message}],
#         stream=True,
#     )
#     for chunk in response:
#         if chunk.choices[0].delta is not None:
#             chunk_message = chunk.choices[0].delta
#             text = chunk_message.content
#             yield f"{text}"

# async def generate_4(message):
#     response = openai_client.chat.completions.create(
#         model="gpt-4",
#         temperature=0,
#         messages=[{"role": "user", "content": message}],
#         stream=True,
#     )
#     for chunk in response:
#         if chunk.choices[0].delta is not None:
#             chunk_message = chunk.choices[0].delta
#             text = chunk_message.content
#             yield f"{text}"