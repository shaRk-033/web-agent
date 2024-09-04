import json
from utils import get_html, write_to_file, generate_prompt_gemini, generate_prompt_to_answer, extract_json_from_response  # Import the new function
from langchain_openai import ChatOpenAI  # Updated import
from langchain_google_genai import ChatGoogleGenerativeAI  # Updated import

def process_form_answers(form_url, user_info):  
    visible_html = get_html(form_url)  

    prompt_gemini = generate_prompt_gemini(visible_html)  

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    response = llm.invoke(prompt_gemini).content  

    json_response = extract_json_from_response(response)  

    write_to_file("gemini_response.json", json_response, as_json=True)  

    prompt_to_answer = generate_prompt_to_answer(response, user_info)  

    llm2 = ChatOpenAI(model="gpt-4o-mini")
    answers = llm2.invoke(prompt_to_answer).content  

    json_matches = extract_json_from_response(answers)
    if json_matches:
        with open("xpaths.json", "w") as json_file:
            json.dump(json_matches, json_file) 


    return json_matches