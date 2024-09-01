import os
import json
from dotenv import load_dotenv
from groq import Groq
import re
import time

load_dotenv()

def initialize_client():
    return Groq(api_key=os.environ.get("GROQ_API_KEY"))

def read_html_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def create_prompt(html_content):
    return f"""
    This is the HTML of a Google Form consisting of questions, options, and input text boxes. Extract all the questions and return them as a JSON object. For each question, include:
    - Relative XPath to the question (similar to the format in the examples below)
    - The question's HTML element (the innermost one that contains the data, i.e., the span classes)
    - If the answer is a text input, include its HTML (the innermost one that contains the data, i.e., the span classes)
    - If the answer consists of radio buttons or multiselect options, return all of its options' HTML (the innermost one that contains the data, i.e., the span classes)

    XPath examples for options:
    "//span[@class='aDTYNe snByac OvPDhc OIC90c' and text()='...']"
    "//div[@class='Zki2Ve' and text()='.']"

    XPath examples for text inputs:
    "//input[@type='text' and @aria-labelledby='i46']"
    "//input[@type='email' and @aria-labelledby='i54']"

    Please format the XPaths in a similar manner to these examples.

    HTML content:
    {html_content}
    """

def get_chat_completion(client, prompt):
    return client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "Output only JSON with questions, options, and input text boxes as described above."
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama-3.1-8b-instant",
    )

def extract_json_from_response(content):
    json_match = re.search(r'```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```', content, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.decoder.JSONDecodeError as e:
            print(f"JSONDecodeError: {e}")
            return None
    else:
        print("No valid JSON found in the response")
        return None

def save_json_to_file(data, file_path):
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

def process_html_to_json(html_file_path, output_json_path):
    client = initialize_client()
    html_content = read_html_file(html_file_path)
    prompt = create_prompt(html_content)
    
    max_retries = 5
    for attempt in range(max_retries):
        chat_completion = get_chat_completion(client, prompt)
        content = chat_completion.choices[0].message.content
        
        chat_completion_dict = extract_json_from_response(content)
        if chat_completion_dict:
            save_json_to_file(chat_completion_dict, output_json_path)
            break
        else:
            print(f"Attempt {attempt + 1} failed, retrying...")
            time.sleep(2)  # Optional: wait for 2 seconds before retrying
    else:
        print("Max retries reached. Failed to get valid JSON.")


process_html_to_json("visible_html_orders.html","init.json")
