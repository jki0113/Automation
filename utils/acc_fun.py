from utils.async_gpt import *
from glob import glob
import json
import pandas as pd
import tempfile
import re
import string
import textract
from docx import Document
from langchain.text_splitter import CharacterTextSplitter


def extract_text_from_docx(filename):
    text = textract.process(filename)
    return text.decode('utf-8-sig')

def preprocess_docx(raw_data, chunk_size):
    glo_text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=chunk_size,
        chunk_overlap=0
    )

    dt = re.split(r'[\n\t]+', raw_data)
    dt =[x for x in dt if x != '']

    unique_dt = []
    for x in dt:
        if x not in unique_dt:
            unique_dt.append(x)

    preprocessed_dt = '\n'.join(unique_dt)
    split_dt = glo_text_splitter.split_text(preprocessed_dt)

    return split_dt

def gpt_glo_list_type(gpt_results):
    raw_ls = []
    for r in gpt_results:
        tmp = re.split(r'\n|-', r.choices[0].message.content)
        tmp = [x.strip() for x in tmp if x != '']
        raw_ls.extend(tmp)
    raw_ls = list(set(raw_ls))
    raw_ls = [item for item in raw_ls if re.search('[가-힣]', item)]
    return raw_ls

def gpt_glo_preprocess(gpt_results):
    glo = []
    for r in gpt_results:
        tmp = r.choices[0].message.content.strip('`').strip('json\n').rstrip('`').strip()
        try:
            dt_json = json.loads(tmp)
            glo.extend(dt_json['glo'])
            
        except json.JSONDecodeError as e:
            logging.error(f"JSONDecodeError: {e} - Data: '{tmp}'")
    
    glo_ls = [item for item in glo if re.search('[가-힣]', item)]
    return glo_ls


def create_glossary(dt):
    create_glo_prompt = """The National Asia Culture Center, an organization that hosts music, theater, and  other performances, has asked you to translate a description of a performance.
        As a translator, you will create a glossary to ensure the consistency of the translation.
        You will extract terms such as names of performances, people, schools, etc. that exist in a given document, paying attention to the following conditions.

        - Exclude terms that have a common meaning, such as dates and times.
        - Extract for unique nouns such as performers, places, events, people, institutions, organizations, etc.
        - In addition, extract terms that translators may need to look up and translate in the source material.
        - For languages that are expressed in units, such as terms (translation terms), extract parentheses and terms in parentheses as well.
        - Exclude terms longer than three words.
        - Extract only terms in Korean.
        - Return the format as the json, as in {'glo': [..., ...]} and the key values in the json should be in the form of a Python list of the refined glossary.

        Create a glossary for the following:
        """
    prompts = [create_glo_prompt + x for x in dt]

    return prompts

        
def refine_glossary(glo_list):
    
    refine_glo_prompt = """As a translator, you will refine the glossary for consistency in translation.
        The refined glossary will filter or refine terms to take into account the following cases

        - Exclude generic words like 'Asia', 'free', 'ticket', etc.
        - Terms in the form '1. first term', '2. second term' should be refined by removing numbers and periods, such as 'first term', 'second term'.
        - Exclude words that have a generic meaning, such as 'issue 5' or 'chapter 1'.
        - Exclude words that have the same meaning but appear as different words due to spacing.
        - Return the format as the json, as in {'glo': [..., ...]} and the key values in the json should be in the form of a Python list of the refined glossary.

        Refine the glossary for the following lists:
        """
    
    if len(glo_list) < 100:
        prompts = [refine_glo_prompt + str(glo_list)]
    else:
        iter = len(glo_list) // 100
        prompts = []
        for i in range(iter+1):
            if len(glo_list) > 100*(i+1):
                prompts.append(refine_glo_prompt + str(glo_list[100*i:100*(i+1)]))
            else:
                prompts.append(refine_glo_prompt + str(glo_list[100*i:]))

    return prompts

def gpt_glo_preprocess(gpt_results):
    glo = []
    for r in gpt_results:
        if r is None:
            next
        else:
            tmp = r.strip('`').strip('json\n').rstrip('`').strip()
            try:
                dt_json = json.loads(tmp)
                glo.extend(dt_json['glo'])
                
            except json.JSONDecodeError as e:
                logging.error(f"JSONDecodeError: {e} - Data: '{tmp}'")
    
    glo_ls = [item for item in glo if re.search('[가-힣]', item)]
    return glo_ls


def run_acc(uploaded_file, chunk_size=400):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name

    # Read word file
    text = extract_text_from_docx(tmp_file_path)

    # Truncate data into chunk-sized chunks 
    preprocess_data = preprocess_docx(raw_data=text, chunk_size=chunk_size)

    # Generate prompt list for creating a glossary
    create_glo_prompt_list = create_glossary(dt=preprocess_data)

    # API request
    async_gpt_result = asyncio.run(process_api_requests_from_prompt_list(
                prompt_list=create_glo_prompt_list,
                model = "gpt-4-0125-preview",
                temperature = .0,
                api_key = OPENAI_KEY,
                request_url = "https://api.openai.com/v1/chat/completions",
                json_mode = True,
                desc = "generating glossary",
                timeout=15
        ))
    
    # Save the number of tokens
    prompt_token_ls = []
    completion_token_ls = []


    # Save results in order
    result = [None] * len(create_glo_prompt_list)
    for gpt_result in async_gpt_result:
        if gpt_result is None:
            continue
        else:
            result[gpt_result[0]] = gpt_result[1][1]['choices'][0]['message']['content']
            prompt_token_ls.append(gpt_result[1][1]['usage']["prompt_tokens"])
            completion_token_ls.append(gpt_result[1][1]['usage']["completion_tokens"])

    # Data preprocessing for 1st glo_list
    glo_ls = gpt_glo_preprocess(gpt_results=result)

    # Generate prompt list for refining a glossary
    refine_glo_prompt_list = refine_glossary(glo_list=glo_ls)

    # API request
    async_gpt_result = asyncio.run(process_api_requests_from_prompt_list(
                prompt_list=refine_glo_prompt_list,
                model = "gpt-4-1106-preview",
                temperature = .0,
                api_key = OPENAI_KEY,
                request_url = "https://api.openai.com/v1/chat/completions",
                json_mode = True,
                desc = "refining glossary",
                timeout=60
        ))
    
    # Save results in order
    refined_result = [None] * len(refine_glo_prompt_list)
    for gpt_result in async_gpt_result:
        if gpt_result is None:
            continue
        else:
            refined_result[gpt_result[0]] = gpt_result[1][1]['choices'][0]['message']['content']
            prompt_token_ls.append(gpt_result[1][1]['usage']["prompt_tokens"])
            completion_token_ls.append(gpt_result[1][1]['usage']["completion_tokens"])

    # Data preprocessing for final glo_list
    final_glo = gpt_glo_preprocess(gpt_results=refined_result)
    
    # Calculate total price
    total_price = sum(prompt_token_ls) * (0.03/1000)+ sum(completion_token_ls) * (0.06/1000)
    price_ls = [str(round(total_price,5))] + [''] * (len(final_glo) - 1)

    df = pd.DataFrame({'vocab': final_glo, 'price': price_ls})

    return df