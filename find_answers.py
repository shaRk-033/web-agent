import os
import json
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def initialize_client():
    return Groq(api_key=os.environ.get("GROQ_API_KEY"))

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def create_prompt(user_input, results_json):
    return f"""
    Based on the following user input and form structure, generate an answers JSON object that matches the user's responses to the form questions.

    User input:
    {user_input}

    Form structure:
    {json.dumps(results_json, indent=2)}

    Generate answers strictly in this following format:
    {{
        "xpaths_options_list": [
            "//span[contains(@class, 'aDTYNe') and text()='...']",
            "//div[@class='Zki2Ve' and text()='...']",
            // ... more simplified XPaths for options ...
        ],
        "xpaths_text_list": {{
            "//input[@type='text' and @aria-labelledby='i1']": "user's text input",
            "//input[@type='email' and @aria-labelledby='i5']": "user's email input",
            // ... more simplified XPaths for text inputs ...
        }}
    }}

    Ensure that all questions are answered based on the user's input and include simplified XPaths that focus on unique identifiers for each element. Use the appropriate XPath format for each type of input (options and text inputs) as shown in the example above. For options, prefer using text content or unique class names. For text inputs, use input types and aria-labelledby attributes when available.
    """

def get_chat_completion(client, prompt):
    return client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that generates JSON objects based on user input and form structures.",
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama-3.1-70b-versatile",
    )

def extract_json_from_response(content):
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content, re.IGNORECASE)
    if json_match:
        json_str = json_match.group(1)
        try:
            json_obj = json.loads(json_str)
            return json_obj
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            print("Extracted JSON string:")
            print(json_str)
    else:
        print("No JSON code block found in the response")
    return None

def save_json_to_file(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)

def generate_answers_json(input_json_path, output_json_path, user_input):
    client = initialize_client()
    results_json = read_json_file(input_json_path)
    prompt = create_prompt(user_input, results_json)
    
    chat_completion = get_chat_completion(client, prompt)
    content = chat_completion.choices[0].message.content
    
    formatted_answers = extract_json_from_response(content)
    if formatted_answers:
        save_json_to_file(formatted_answers, output_json_path)
        print(f"Formatted answers generated successfully and saved to {output_json_path}")
    else:
        print("Failed to generate valid JSON.")
        print("Generated content:", content)

if __name__ == "__main__":
    user_input = """
    Hey, I am an existing customer, and I want to order pens and notebooks of red and blue colors. 
    Quantity of the items should be 4. As per details about me, I'm Kavan, and I'm available at 
    9548565487 / kavan@gmail.com. Preferred mode of communication is either phone or email.
    """
    generate_answers_json("./init.json", "./answers.json", user_input)

