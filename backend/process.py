import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from selenium import webdriver
import os
import time
from dotenv import load_dotenv
from utils import click
from get_html import get_html
import re
import json
from selenium.common.exceptions import NoSuchElementException, TimeoutException 

load_dotenv()

def read_html_file(file_path):
    with open(file_path, "r") as f:
        return f.read()

def write_to_file(file_path, content, as_json=False):
    with open(file_path, "w") as f:
        if as_json:
            json.dump(content, f, indent=4)
        else:
            f.write(content)

def extract_json_from_response(response):
    json_pattern = re.compile(r'```json\s*(.*?)\s*```', re.DOTALL)
    json_match = json_pattern.search(response)
    if json_match:
        return json.loads(json_match.group(1))
    else:
        print("No JSON content found in the string.")
        return None

def generate_prompt_gemini(visible_html):
    return f"""This is the HTML of a Google form consisting of questions, options, and input text boxes. Extract all the questions.
    While returning questions, for each of them include:
    - The question's HTML element (the innermost one that contains the data, e.g., the span classes)
    - If the answer to be filled is a text input, include its HTML (the innermost one that contains the data, e.g., the span classes)
    - If the answer to be filled are radio buttons or multiselect options, return all of its options' HTML (the innermost one that contains the data, e.g., the span classes)
    The HTML of the page is: 
    {visible_html}"""

def generate_prompt_to_answer(response, user_info):
    return f"""A user is trying to fill a Google form that has the following questions, answers, and options:
{response}

The user has provided the following info: 
{user_info}
Based on this info, can you say what answers they would have selected for each question?

Return questions, options/answers (include HTML), and XPath in JSON format.
Note:
- For text and email inputs, specify option HTML, text content, and XPath that needs to be filled.

The JSON format should be like this:
[
## For clickable options
{{"question": "",
  "selected_options":[
  {{"html":"","xpath":""}}
  ]
}},
## For text inputs and email inputs
{{"question": "",
  "text_input":{{
  "textcontent":"",
  "html":"","xpath":""
  }}
}}
]
"""

async def process_form(user_info, form_url):
    max_retries = 3  # Maximum number of retries
    for attempt in range(max_retries):
        try:
            visible_html = await asyncio.to_thread(get_html, form_url)
            
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
            prompt_gemini = generate_prompt_gemini(visible_html)
            
            start = time.time()
            response = await asyncio.to_thread(llm.invoke, prompt_gemini)
            response_content = response.content
            print("time taken by gemini", time.time() - start)
            
            await asyncio.to_thread(write_to_file, "gemini_response.json", response_content, as_json=True)

            prompt_to_answer = generate_prompt_to_answer(response_content, user_info)
            llm2 = ChatOpenAI(model="gpt-4o-mini")
            answers = await asyncio.to_thread(llm2.invoke, prompt_to_answer)
            answers_content = answers.content

            data = extract_json_from_response(answers_content)
            if data:
                await asyncio.to_thread(write_to_file, "answers.json", data, as_json=True)

                xpaths_options_list = []
                xpaths_text_list = {}

                for item in data:
                    question = item.get("question", "")
                    if "selected_options" in item and item["selected_options"] is not None: 
                        for option in item["selected_options"]:
                            xpaths_options_list.append(option["xpath"])
                    elif "text_input" in item and item["text_input"] is not None:
                        xpaths_text_list[item["text_input"]["xpath"]] = item["text_input"]["textcontent"]

                print("xpaths_options_list =", xpaths_options_list)
                print("xpaths_text_list =", xpaths_text_list)

                xpaths_data = {
                    "xpaths_options_list": xpaths_options_list,
                    "xpaths_text_list": xpaths_text_list
                }
                await asyncio.to_thread(write_to_file, "xpaths.json", xpaths_data, as_json=True)

                await asyncio.to_thread(click, xpaths_options_list, xpaths_text_list, form_url)
                
                verification_html = await asyncio.to_thread(get_html, form_url)
                if not re.search(r'<button[^>]*type=["\']submit["\'][^>]*>', verification_html, re.IGNORECASE):  # Check for submit button
                    print("Form submitted successfully, submit button is no longer present.")
                else:
                    print("Form submission may not have been successful, submit button is still present.")
                
                break  
        
        except (NoSuchElementException, TimeoutException) as e:  
            print(f"Attempt {attempt + 1} failed due to {type(e).__name__}. Retrying...")
            if attempt == max_retries - 1:
                print("Max retries reached. Exiting process.")
                raise  # Re-raise the exception after max retries
