import os
import json
from dotenv import load_dotenv
from groq import Groq
import re

load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

with open('visible_html_orders.html', 'r') as file:
    html_content = file.read()

prompt = """
this is the html of a google form consisting of question,options,input text boxes ..from all of extract all the questions
while returning questions for each of them include
-the question's html element (the inner most one that contains the data.. the span classes)
-if the answer to be filled is text input,then include its html (the inner most one that contains the data.. the span classes)
-if the answer to be filled are radio buttons,multiselect options,then return all of its options html (the inner most one that contains the data.. the span classes)
return json object not code
"""

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": f"{prompt}\n\n{html_content}",
        }
    ],
    model="llama-3.1-70b-versatile",
)

content = chat_completion.choices[0].message.content
print(content) 

json_match = re.search(r'```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```', content, re.DOTALL)
if json_match:
    json_str = json_match.group(1)
    chat_completion_dict = json.loads(json_str)  

    with open('results.json', 'w') as json_file:
        json.dump(chat_completion_dict, json_file, indent=4)
else:
    print("No valid JSON found in the response")