from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from selenium import webdriver
import os
import time
from dotenv import load_dotenv
from utils import click
import re
import json

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

    The user has provided this information: 
    {user_info}

    Based on the above information, can you determine what answers the user would have chosen for each question?

    Return questions, options/answers (include HTML), and XPath in JSON format.
    Note:
    - For text and email inputs, specify the option HTML, text content, and XPath that needs to be filled.
    - xpath shouldnt contain contains(text())

    The JSON format should be like this:
    [
    ## For clickable options
    {{"question": "",
    "selected_options":[
    {{"html":"","xpath":""}}
    ],}}
    ## For text inputs and email inputs
    {{"question": "",
    "text_input":{{
    "textcontent":"",
    "html":"","xpath":""
    }}
    }}]
    """

def process_form(user_info, form_url):
    visible_html = read_html_file("visible_html_orders.html")

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    prompt_gemini = generate_prompt_gemini(visible_html)
    
    start = time.time()
    response = llm.invoke(prompt_gemini).content
    print("time taken by gemini", time.time() - start)
    
    write_to_file("gemini_response.json", response, as_json=True)

    prompt_to_answer = generate_prompt_to_answer(response, user_info)
    llm2 = ChatOpenAI(model="gpt-4o-mini")
    answers = llm2.invoke(prompt_to_answer).content

    data = extract_json_from_response(answers)
    if data:
        write_to_file("answers.json", data, as_json=True)

        xpaths_options_list = []
        xpaths_text_list = {}

        for item in data:
            question = item.get("question", "")
            if "selected_options" in item:
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
        write_to_file("xpaths.json", xpaths_data, as_json=True)

        click(xpaths_options_list, xpaths_text_list, form_url)

if __name__ == "__main__":
    user_info = """Hey, I am an existing customer, and I want to order pens and notebooks of red and blue colors. 
    Quantity of the items should be 4. As per details about me, I’m Kavan, and I’m available at 9548565487 / kavan@gmail.com. Preferred mode of communication is either phone or email."""
    form_url = 'https://docs.google.com/forms/d/e/1FAIpQLSd9gli7KqnYFNkrc_PWNxvmhi7ZJz2jPp0qTsceqT7lkIBo2Q/viewform'
    process_form(user_info, form_url)

