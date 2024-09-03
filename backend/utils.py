from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
import os

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

