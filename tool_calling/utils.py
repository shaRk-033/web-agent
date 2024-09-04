from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

import time
import json
import re
import os

def get_html(form_url):
    try:
        driver = webdriver.Chrome()
        driver.get(form_url)
        time.sleep(1)
        visible_html = driver.execute_script("return document.body.innerHTML;")

        with open("form.html", "w") as f:
            f.write(visible_html)
        
        return visible_html 

    except WebDriverException as e:
        print(f"WebDriverException occurred: {e}")
    except TimeoutException as e:
        print(f"TimeoutException occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        driver.quit()
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
os.makedirs("screenshots", exist_ok=True)

def click_all_visible_elements(xpaths_options_list, xpaths_text_list, driver, visited):
    wait = WebDriverWait(driver, 10) 

    for i, xpath in enumerate(xpaths_options_list):
        if visited[i] == 0:
            try:
                element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                element.click()
                visited[i] = 1
                screenshot_path = f"screenshots/element_click_{i}.png"
                driver.save_screenshot(screenshot_path) 
                log_event({
                    "type": "click",
                    "xpath": xpath,
                    "timestamp": time.time(),
                    "screenshot": screenshot_path 
                })
            except (TimeoutException, NoSuchElementException):
                print(f"Element not interactable or not found: {xpath}")

    for i, (xpath, text) in enumerate(xpaths_text_list.items(), start=len(xpaths_options_list)):
        if visited[i] == 0:
            try:
                input_element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                input_element.clear()
                input_element.send_keys(text)
                visited[i] = 1
                screenshot_path = f"screenshots/text_input_{i}.png"
                driver.save_screenshot(screenshot_path) 
                log_event({
                    "type": "textInput",
                    "xpath": xpath,
                    "text": text,
                    "timestamp": time.time(),
                    "screenshot": screenshot_path 
                })
            except (TimeoutException, NoSuchElementException):
                print(f"Element not interactable or not found: {xpath}")

def click(xpaths_options_list, xpaths_text_list, form_url):
    with open("events.json", "w") as f:
        f.write("")

    visited = [0] * (len(xpaths_options_list) + len(xpaths_text_list))
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(form_url)
    time.sleep(1)
    visible_html = driver.execute_script("return document.body.innerHTML;")
    log_event({
        "type": "load",
        "url": form_url,
        "timestamp": time.time(),
        "screenshot": "screenshots/page_load.png"  
    })
    driver.save_screenshot("screenshots/page_load.png") 
    for i in range(6):
        driver.execute_script("window.scrollBy(0, 180);")
        log_event({
            "type": "scroll",
            "scrollY": 180,
            "timestamp": time.time(),
            "screenshot": f"screenshots/scroll_{i}.png"  
        })
        driver.save_screenshot(f"screenshots/scroll_{i}.png") 
        click_all_visible_elements(xpaths_options_list, xpaths_text_list, driver, visited)
    submit_button_xpath = "//span[text()='Submit']"  
    
    try:
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, submit_button_xpath))
        )
        submit_button.click()
        driver.save_screenshot("screenshots/form_submit.png")
        log_event({
            "type": "click",
            "xpath": submit_button_xpath,
            "timestamp": time.time(),
            "screenshot": "screenshots/form_submit.png" 
        })
        print("Form submitted successfully.")
    except TimeoutException:
        print("Submit button not found or not clickable.")
    except NoSuchElementException:
        print("Submit button not found.")

def log_event(event):
    with open("events.json", "a") as f:
        json.dump(event, f)
        f.write("\n")

