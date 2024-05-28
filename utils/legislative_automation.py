# 번역 1팀 조문체계 처리 자동화

from stqdm import stqdm
from utils.async_gpt import *
import os
import json

def run_legislative_automation(df, selected_col, selected_country):
    df['translation'] = ''
    df['structure'] = ''
    df['price'] = .0

    # 편제 추출 및 번역
    df = extract_legislative(df, selected_col, selected_country)

    # 용어집 추출
    """용어집 추출은 그때 그떄 PM들이 자동화 페이지에서 할 수 있도록..."""
    

    return df

# def apply_voacb(df):
#     """전달 받은 용어집으로 용어집 추출 -> 일단 진행하지 않는것으로 결정 됨"""
#     return

def extract_legislative(df, selected_col, selected_country):
    prompt_list = [make_prompt_extract_legislative(i, selected_country) for i in df[selected_col]]
    print('=' * 100)
    print(prompt_list[15])
    print('=' * 100)
    async_gpt_result = asyncio.run(process_api_requests_from_prompt_list(
            prompt_list=prompt_list[:],
            model='gpt-4o',
            temperature=.0,
            api_key=os.getenv("OPENAI_GPT_API_KEY"),
            request_url="https://api.openai.com/v1/chat/completions",
            json_mode=True,
            desc="번역2팀 편제처리 자동화 - 조문체계 추출...",
            timeout=180,
            seed=42,
    ))

    result = [None] * len(prompt_list)
    price = [None] * len(prompt_list)

    # 결과 파싱
    for gpt_result in stqdm(async_gpt_result, desc="결과 파싱 중"):
        if gpt_result is None:
            continue
        else:
            result[gpt_result[0]] = gpt_result[1][1]['choices'][0]['message']['content']
            price[gpt_result[0]] = (gpt_result[1][1]['usage']['prompt_tokens'] * 0.005 / 1000) + (gpt_result[1][1]['usage']['completion_tokens'] * 0.015 / 1000)

    # 파싱된 결과 json 변환
    result_dict_list = []
    for json_string, price in zip(result, price):
        data = json.loads(json_string)
        data['price'] = price
        result_dict_list.append(data)

    df['translation'] = [item['translation'] for item in result_dict_list]
    df['structure'] = ['\n'.join(f"{k}: {', '.join(v)}" for k, v in item['structure'].items()) for item in result_dict_list]
    df['price'] = [item['price'] for item in result_dict_list]
    df['translation'] = [item['translation'].replace('-', '').replace(';', '').replace(':', '').strip() for item in result_dict_list]
    
    return df

def make_prompt_extract_legislative(text, country):
    if country.strip() == "미국":
        country_code = 'U.S.'
    elif country.strip() == "호주":
        country_code = 'Austrailian'
    elif country.strip() == "싱가포르":
        country_code = 'Singaporean'
    elif country.strip() == "영국":
        country_code = 'U.K.'
    elif country.strip() == "캐나다":
        country_code = 'Canadian'
    elif country.strip() == "케냐":
        country_code = 'Kenyan'
    elif country.strip() == "스리랑카":
        country_code = 'Sri Lankan'
    elif country.strip() == "뉴질랜드":
        country_code = 'New Zealand'
    elif country.strip() == "인도":
        country_code = 'India'
    elif country.strip() == "유럽연합":
        country_code = 'EU'
    elif country.strip() == "캄보디아":
        country_code = 'Cambodian'
    elif country.strip() == "필리핀":
        country_code = 'Philippines'
    elif country.strip() == "말레이시아":
        country_code = 'Malay'
    else:
        raise ValueError("머고")
    
    prompt=f"""
### Instruction
Your role as a legal translation expert is to extract the text from the given legislation in accordance with the {country_code} Legislative Structure and translate it accordingly.
1. Refer to the provided Austrailian Legislative Structure and identify any terms that exactly match or are variations of the structure such as 'Chapter I', 'Part 1', 'Division 2', etc., within the given text. Extract only these terms.
    - Ensure to extract each term individually rather than as combined structures.
    - You must never extract terms that are not included in the ### {country_code} Legislative Structure.
2. List and translate all extracted terms, ensuring to capture any relevant variations.
3. Translate the following sentences based on the extracted terms.
   - The tone of the translation should match legal documents, using informal constructions such as '~한다', '~이다' instead of formal ones like '~합니다', '~입니다'.
   - If the text is too short or if there are no extracted legislative terms, proceed with the translation in accordance with legal document standards.
4. Respond in JSON format, where:
   - The 'structure' key should contain the extracted terms. Each key should represent the legislative structure terms extracted from the text and the translated result according to the structure.
   - The 'translation' key should contain the translated text from Legal text
   - If a term appears multiple times in the text and requires different translations, add these variations as separate strings in the list under the respective key.
   - example: {{"structure": {{"§ 73.1400": ["제73.1400조"], "(a)": ["제1항"], "(a)(1)": ["제1항 제1호"], "(b)": ["제2항"]}}, "translation": "제1항 신원 및 규격. 색소 첨가물 피로필라이트는 제73.1400조 제1항 제1호 및 제2항의 요구 사항에 부합하는 신원 및 규격을 준수해야 합니다."}}
5. If the type is not present in the {country_code} Legislative Structure, do not extract any results, and do not arbitrarily handle items that are not listed in the {country_code} Legislative Structure.
6. This task is very important, and any errors can lead to claims for damages and legal penalties, so please work with utmost accuracy and care.
*Once again, do not extract any items outside of the ### {country_code} Legislative Structure."""
    prompt += '\n\n'
    prompt += legislative_dict[country]
    prompt += '\n\n'
    prompt += f"### Legal text: "
    prompt += f"{text}"

    return prompt

legislative_dict={
    '미국' : """### U.S. Legislative Structure:

source: Title (Numeric)
target: 제(Numeric)편
example: Title 5 → 제5편

source: Chapter (Numeric)
target: 제(Numeric)장
example: Chapter 1 → 제1장

source: Subchapter (Alphabetic - Uppercase)
target: 제(Numeric)절
example: Subchapter A → 제1절

source: Part (Alphabetic - Uppercase)
target: 제(Numeric)부
example: Part C → 제3부

source: Subpart (Roman Numeral)
target: 제(Numeric)관
example: Subpart I → 제1관

source: Section (Numeric)
target: 제(Numeric)조
example: Section 4 → 제4조, Section 18 → 제18조

source: § (Numeric)
target: 제(Numeric)조
example: § 15 → 제15조, § 3.25 → 제3.25조

source: SEC. (Numeric)
target: 제(Numeric)조
example: SEC. 3 → 제3조, SEC. 7 → 제7조

source: ((Alphabetic - Lowercase))
target(when appearing at the beginning of the sentence): ((Alphabetic - Lowercase))
example: (c) → (c)
target(when not appearing at the beginning of the sentence): 제(Alphabetic - Lowercase)항
example: (d) → 제(d)항

source: ((Numeric))
target(when appearing at the beginning of the sentence): ((Numeric))
example: (8) → (8)
target(when not appearing at the beginning of the sentence): 제((Numeric))호
example: (12) → 제(12)호

source: ((Alphabetic - Uppercase))
target(when appearing at the beginning of the sentence): ((Alphabetic - Uppercase))
example: (A) → (A)
target(when not appearing at the beginning of the sentence): ((Alphabetic - Uppercase))목
example: (B) → (B)목

source: ((Roman Numeral - Lowercase))
target: ((Roman Numeral - Lowercase))
example: (i) → (i), (ii) → (ii)

source: ((Roman Numeral - Uppercase))
target: ((Roman Numeral - Uppercase))
example: (I) → (I), (II) → (II)

source: ((Alphabetic - Lowercase)(Alphabetic - Lowercase))
target: ((Alphabetic - Lowercase)(Alphabetic - Lowercase))
example: (aa) → (aa)

source: ((Alphabetic - Uppercase)(Alphabetic - Uppercase))
target: ((Alphabetic - Uppercase)(Alphabetic - Uppercase))
example: (AA) → (AA)""",
    "호주": """### Austrailian Legislative Structure:

source: Chapter (Roman Numeral - Uppercase)
target: 제(Roman numeral - Uppercase)편
example: Chapter I → 제I편

source: Part (Numeric)
target: 제(Numeric)장
example: Chapter 1 → 제1장

source: Division (Numeric)
target: 제(Numeric)절
example: Division 2 → 제2절

source: Subdivision (Alphabetic - Uppercase)
target: 제(Alphabetic - Uppercase)관
example: Subdivision D → 제D관

source: (Numeric)
target: 제(Numeric)조
example: 2 → 제2조

source: ((Numeric))
target(when appearing at the beginning of the sentence): ((Numeric))
example: (2) → (2)
target(when not appearing at the beginning of the sentence): 제((Numeric))항
example: (1) → 제(1)항

source: ((Alphabetic - Lowercase))
target(when appearing at the beginning of the sentence): ((Alphabetic - Lowercase))
example: (c) → (c)
target(when not appearing at the beginning of the sentence): 제((Alphabetic - Lowercase))호
example: (d) → 제(d)호

source: ((Roman Numeral - Lowercase))
target(when appearing at the beginning of the sentence): ((Roman Numeral - Lowercase))
example: (i) → (i), (ii) → (ii)
target(when not appearing at the beginning of the sentence): ((Roman Numeral - Lowercase))목
example: (i) → (i)목, (ii) → (ii)""",
    "싱가포르": """### Singaporean Legislative Structure:

source: Part (Numeric)
target: 제(Numeric)장
example: Part 1 → 제1장

source: Division (Numeric)
target: 제(Numeric)절
example: Division 2 → 제2절

source: (Numeric).
target: 제(Numeric)조
example: 2. → 제2조

source: (Numeric)(Alphabetic - Uppercase)
target: 제(Numeric)(Alphabetic - Uppercase)조
example: 12I → 제12I조

source: Section (Numeric)
target: 제(Numeric)조
example: Section 12 → 제12조

source: Article (Numeric)
target: 제(Numeric)조
example: Article 1 → 제1조

source: ((Numeric))
target(when appearing at the beginning of the sentence): ((Numeric))
example: (2) → (2)
target(when not appearing at the beginning of the sentence): 제((Numeric))항
example: (1) → 제(1)항

source: ((Numeric)(Alphbetic - Uppercase))
target(when appearing at the beginning of the sentence): ((Numeric)(Alphabetic - Uppercase))
example: (1AA) → (1AA)
target(when not appearing at the beginning of the sentence): 제((Numeric)(Alphabetic - Uppercase))항
example: (1AA) → 제(1AA)항

source: ((Alphabetic - Lowercase))
target(when appearing at the beginning of the sentence): ((Alphabetic - Lowercase))
example: (c) → (c)
target(when not appearing at the beginning of the sentence): 제((Alphabetic - Lowercase))호
example: (d) → 제(d)호

source: ((Roman Numeral - Lowercase))
target(when appearing at the beginning of the sentence): ((Roman Numeral - Lowercase))
example: (i) → (i), (ii) → (ii)
target(when not appearing at the beginning of the sentence): ((Roman Numeral - Lowercase))목
example: (i) → (i)목, (ii) → (ii)목

source: ((Alphabetic - Uppercase))
target: ((Alphabetic - Uppercase))
example: (A) → (A)""",
    "영국": """### U.K. Legislative Structure:
    
source: Part (Numeric)
target: 제(Numeric)편
example: Part 1 → 제1편

source: Chapter (Numeric)
target: 제(Numeric)장
example: Chapter 2 → 제2장

source: (Numeric).
target: 제(Numeric)조
example: 2. → 제2조

source: Section (Numeric)
target: 제(Numeric)조
example: Section 12 → 제12조

source: ((Numeric))
target(when appearing at the beginning of the sentence): ((Numeric))
example: (2) → (2)
target(when not appearing at the beginning of the sentence): 제((Numeric))항
example: (1) → 제(1)항

source: ((Alphabetic - Lowercase))
target(when appearing at the beginning of the sentence): ((Alphabetic - Lowercase))
example: (c) → (c)
target(when not appearing at the beginning of the sentence): 제((Alphabetic - Lowercase))호
example: (d) → 제(d)호

source: ((Roman Numeral - Lowercase))
target(when appearing at the beginning of the sentence): ((Roman Numeral - Lowercase))
example: (i) → (i), (ii) → (ii)
target(when not appearing at the beginning of the sentence): ((Roman Numeral - Lowercase))목
example: (i) → (i)목, (ii) → (ii)목""",
    "캐나다": """### Canadian Legislative Structure:

source: Part (Roman Numeral - Uppercase)
target(when appearing at the beginning of the sentence): 제(Roman Numeral - Uppercase)장
example: Part II → 제II장
target(when not appearing at the beginning of the sentence): 제(Numeric)장
example: Part I → 제1장

source: (Numeric)
target: 제(Numeric)조
example: 2 → 제2조

source: ((Numeric))
target(when appearing at the beginning of the sentence): Circled Digit
example: (2) → ②
target(when not appearing at the beginning of the sentence): 제(Numeric)항
example: (1) → 제1항

source: ((Alphabetic - Lowercase))
target(when appearing at the beginning of the sentence): (Numeric).
example: (c) → 3.
target(when not appearing at the beginning of the sentence): 제(Numeric)호
example: (d) → 제4호

source: ((Roman Numeral - Lowercase))
target(when appearing at the beginning of the sentence): (Korean Consonant).
example: (i) → 가., (ii) → 나.
target(when not appearing at the beginning of the sentence): (Korean Consonant)목
example: (i) → 가목, (ii) → 나목

source: ((Alphabetic - Uppercase))
target: (Numeric))
example: (A) → 1)""",
    "케냐": """### Kenyan Legislative Structure:

source: Part (Numeric)
target: 제(Numeric)장
example: Part 1 → 제1장

source: (Numeric).
target: 제(Numeric)조
example: 2. → 제2조

source: Section (Numeric)
target: 제(Numeric)조
example: Section 3 → 제3조

source: ((Numeric))
target(when appearing at the beginning of the sentence): ((Numeric))
example: (2) → (2)
target(when not appearing at the beginning of the sentence): 제((Numeric))항
example: (1) → 제(1)항

source: ((Alphabetic - Lowercase))
target(when appearing at the beginning of the sentence): ((Alphabetic - Lowercase))
example: (c) → (c)
target(when not appearing at the beginning of the sentence): 제((Alphabetic - Lowercase))호
example: (d) → 제(d)호

source: ((Roman Numeral - Lowercase))
target(when appearing at the beginning of the sentence): ((Roman Numeral - Lowercase))
example: (i) → (i), (ii) → (ii)
target(when not appearing at the beginning of the sentence): ((Roman Numeral - Lowercase))목
example: (i) → (i)목, (ii) → (ii)목""",
    "스리랑카": """### Sri Lankan Legislative Structure:

source: Part (Roman Numeral - Uppercase)
target(when appearing at the beginning of the sentence): 제(Roman Numeral - Uppercase)편
example: Part I → 제I편
target(when not appearing at the beginning of the sentence): 제(Numeric)편
example: Part III → 제3편

source: Chapter (Numeric)
target: 제(Numeric)장
example: Chapter 2 → 제2장

source: (Numeric):
target: 제(Numeric)조
example: 2: → 제2조

source: ((Numeric))
target(when appearing at the beginning of the sentence): Cirlced Digit
example: (2) → ②
target(when not appearing at the beginning of the sentence): 제(Numeric)항
example: (1) → 제1항

source: ((Alphabetic - Lowercase))
target(when appearing at the beginning of the sentence): (Numeric).
example: (c) → 3.
target(when not appearing at the beginning of the sentence): 제(Numeric)호
example: (d) → 제4호

source: ((Roman Numeral - Lowercase))
target(when appearing at the beginning of the sentence): (Korean Consonant).
example: (i) → 가., (ii) → 나.
target(when not appearing at the beginning of the sentence): (Korean Consonant)목
example: (i) → 가목, (ii) → 나목""",
    "뉴질랜드":"""### New Zealand Legislative Structure
 
source: Part (Numeric)
target: 제(Numeric)장
example: Part 1 → 제1장
 
source: (Numeric).
target: 제(Numeric)조
example: 2. → 제2조
 
source: Section (Numeric)
target: 제(Numeric)조
example: Section 2
 
source: Article (Numeric)
target: 제(Numeric)조
example: Article 2 → 제2조
 
source: Section (Numeric)(Alphabetic - Uppercase)
target: 제(Numeric)(Alphabetic - Uppercase)항
example: Section 12I → 제12I조
 
source: Article (Numeric)(Alphabetic - Uppercase)
target: 제(Numeric)(Alphabetic - Uppercase)항
example: Article 12I → 제12I조
 
source: ((Numeric))
target: ((Numeric))
example: (4) → (4)
 
source: ((Numeric))
target: 제((Numeric))항
example: (4) → 제(4)항
 
source: ((Numeric)(Alphabetic - Uppercase))
target: ((Numeric)(Alphabetic - Uppercase))
example: (4A) → (4A)
 
source: ((Numeric)(Alphabetic - Uppercase))
target: 제((Numeric)(Alphabetic - Uppercase))항
example: (4A) → 제(4A)항
 
source: ((Numeric)(Alphabetic - Uppercase)(Alphabetic - Uppercase))
target: ((Numeric)(Alphabetic - Uppercase)(Alphabetic - Uppercase))
example: (1AA)→ (1AA)
 
source: ((Numeric)(Alphabetic - Uppercase)(Alphabetic - Uppercase))
target: 제((Numeric)(Alphabetic - Uppercase)(Alphabetic - Uppercase))항
example: (1AA)→ 제(1AA)항
 
source: ((Alphabetic - Lowercase))
target(when appearing at the beginning of the sentence): ((Alphabetic - Lowercase))
example: (c) → (c)
source: ((Alphabetic - Lowercase))
target(when not appearing at the beginning of the sentence): 제((Alphabetic - Lowercase))호
example: (d) → 제(d)호
 
source: ((Roman Numeral - Lowercase))
target(when appearing at the beginning of the sentence): ((Roman Numeral - Lowercase))
example: (i) → (i), (ii) → (ii)
target(when not appearing at the beginning of the sentence): ((Roman Numeral - Lowercase))목
example: (i) → (i)목, (ii) → (ii)목""",
    "인도":"""### India Legislative Structure: 

source: Part (Roman Numeral - Uppercase) 
target: 제(Roman Numeral - Uppercase)편 
example: Part I → 제I편, Part II → 제II편 

source: Chapter (Roman Numeral - Uppercase) 
target: 제(Numeric)장 
example: Chapter II → 제2장, Chapter III → 제3장 

source: (Numeric). 
target: 제(Numeric)조 
example: 1. → 제1조, 2. → 제2조 

source: section (Numeric) 
target: 제(Numeric)조 
example:  section 2 → 제2조 

source: ((Numeric)) 
target(when appearing at the beginning of the sentence): -(Numeric) 
example:  (2) → (2) 
target(when not appearing at the beginning of the sentence): 제(Numeric)항 
example:  (2) → 제(2)항 

source: ((Alphabetic - Lowercase)) 
target(when appearing at the beginning of the sentence): ((Alphabetic - Lowercase)) 
example: (b) → (b) 
target(when not appearing at the beginning of the sentence): 제(Alphabetic - Lowercase)호 
example: (b) → 제(b)호 

source: ((Roman Numeral - Lowercase)) 
target(when appearing at the beginning of the sentence): ((Roman Numeral - Lowercase)) 
example: (ii) → (ii) 
target(when not appearing at the beginning of the sentence): (Roman Numeral - Lowercase)목 
example: (ii) → (ii)목 

source: ((Alphabetic - Uppercase)) 
target: ((Alphabetic - Uppercase)) 
example: (B) → (B)""",
    "유럽연합": """### EU Structure: 

source: PART (Numeric) 
target: 제(Numeric)편 
example: PART 5 → 제5편 

source: PPART (Roman Numeral) 
target: 제(Roman Numera)편 
example: PART I → 제I편 

source: TITLE (Numeric) 
target: 제(Numeric)부 
example: TITLE 5 → 제5부 

source: TITLE (Roman Numeral) 
target: 제(Roman Numeral)부 
example: TITLE I → 제I부 

source: CHAPTER (Numeric) 
target: 제(Numeric)장 
example: CHAPTER 1 → 제1장 

source: CHAPTER (Roman Numeral) 
target: 제(Roman Numeral)장 
example: CHAPTER I → 제I장 

source: Section (Numeric) 
target: 제(Numeric)절 
example: Section 4 → 제4절 

source: Article (Numeric) 
target: 제(Numeric)조 
example: Article 4 → 제4조 

source: (Numeric). 
target: target(when appearing at the beginning of the sentence): (Numeric). 
example: 1. → 1. 
target: target(when not appearing at the beginning of the sentence): 제(Numeric)항 
example: 1. → 제1항 

source: ((Numeric)) 
target: target(when appearing at the beginning of the sentence): ((Numeric)) 
example: (8) → (8) 
target: target(when not appearing at the beginning of the sentence): 제((Numeric))호 
example: (9) → 제(9)호 

source: ((Alphabetic - Lowercase)) 
target: target(when appearing at the beginning of the sentence): ((Alphabetic - Lowercase)) 
example: (a) → (a) 
target: target(when not appearing at the beginning of the sentence): ((Alphabetic - Lowercase))목 
example: (a) → (a)목""",
    "캄보디아": """### Cambodian Legislative Structure: 

source: Title (Roman Numeral - Uppercase) 
target: 제(Roman Numeral - Uppercase)편 
example: Title I → 제I편, Title III → 제III편 

source: Chapter (Roman Numeral - Uppercase) 
target: 제(Roman Numeral - Uppercase)장 
example: Chapter II → 제2장, Chapter III → 제3장 

source: Chapter (Numeric) 
target: 제(Numeric)장 
example: Chapter 1 → 제1장, Chapter 5 → 제5장 

source: section (Numeric) 
target: 제(Numeric)절 
example:  section 2 → 제2절 

source: Article (Numeric) 
target: 제(Numeric)조 
example:  Article 2 → 제2조 

source: (Numeric) 
target: 제(Numeric)항 
example: 1 → 제1항, 2 → 제2항 

source: ((Alphabetic - Lowercase)) 
target(when appearing at the beginning of the sentence): ((Alphabetic - Lowercase)) 
example: (b) → (b) 
target(when not appearing at the beginning of the sentence): 제(Numeric)호 
example: (a)→ 제1호, (b)→ 제2호 

source: ((Roman Numeral - Lowercase)) 
target(when appearing at the beginning of the sentence): ((Roman Numeral - Lowercase)) 
example: (ii) → (ii) 
target(when not appearing at the beginning of the sentence): (Korean Consonant)목 
example: (ii) → 나목 """,
    "필리핀": """### Philippines Structure: 

source: Part (Numeric) 
target: 제(Numeric)편 
example: Part 5 → 제5편 

source: Part (Roman Numeral) 
target: 제(Roman Numera)편 
example: Part I → 제I편 

source: Title (Numeric) 
target: 제(Numeric)편 
example: Title 5 → 제5편 

source: Title (Roman Numeral) 
target: 제(Roman Numeral)편 
example: Title I → 제I편 

source: Chapter (Numeric) 
target: 제(Numeric)장 
example: Chapter 1 → 제1장 

source: Chapter (Roman Numeral) 
target: 제(Roman Numeral)장 
example: Chapter I → 제I장 

source: Section (Numeric) 
target: 제(Numeric)조 
example: Section 4 → 제4조 

source: Article (Numeric) 
target: 제(Numeric)조 
example: Article 4 → 제4조 

source: (Numeric). 
target: 제(Numeric)조 
example: 1. → 제1조 

source: ((Alphabetic - Lowercase)) 
target: target(when appearing at the beginning of the sentence): ((Alphabetic - Lowercase)) 
example: (a) → (a) 
target: target(when not appearing at the beginning of the sentence): 제((Alphabetic - Lowercase))항 
example: (a) → 제(a)항 

source: ((Numeric)) 
target: target(when appearing at the beginning of the sentence): ((Numeric)) 
example: (8) → (8) 
target: target(when not appearing at the beginning of the sentence): 제((Numeric))호 
example: (9) → 제(9)호 

source: ((Roman Numeral - Lowercase)) 
target: target(when appearing at the beginning of the sentence): ((Roman Numeral - Lowercase)) 
example: (i) → (i) 
target: target(when not appearing at the beginning of the sentence): ((Roman Numeral - Lowercase))목 
example: (i) → (i)목 """,
    "말레이시아": """### Malay Structure:
    
source: PART (Numeric) 
target: 제(Numeric)장 
example: PART 5 → 제5장 

source: PART (Roman Numeral) 
target: 제(Roman Numera)장 
example: PART I → 제I장 

source: CHAPTER (Numeric) 
target: 제(Numeric)장 
example: CHAPTER 1 → 제1장 

source: CHAPTER (Roman Numeral) 
target: 제(Roman Numeral)장 
example: CHAPTER I → 제I장 

source: Section (Numeric) 
target: 제(Numeric)절 
example: Section 4 → 제4절 

source: (Numeric). 
target: 제(Numeric)조 
example: 1. → 제1조 

source: (Numeric)(Alphabetic - Upercase). 
target: 제(Numeric)(Alphabetic - Upercase)조 
example: 8A. → 제8A조 

source: ((Numeric)) 
target: 제((Numeric))항 
example: (1) → 제(1)항 

source: ((Alphabetic - Lowercase)) 
target: target(when appearing at the beginning of the sentence): ((Alphabetic - Lowercase)) 
example: (a) → (a) 
target: target(when not appearing at the beginning of the sentence): 제((Alphabetic - Lowercase))호 
example: (a) → 제(a)호 

source: ((Roman Numeral)) 
target: target(when appearing at the beginning of the sentence): ((Roman Numeral)) 
example: (i) → (i) 
target: target(when not appearing at the beginning of the sentence): ((Roman Numeral))목 
example: (i) → (i)목 """
}
