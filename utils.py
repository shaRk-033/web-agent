from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

# Iterate over each xpath in the list and click the corresponding element
def click_all_visible_elements(xpaths_options_list, xpaths_text_list, driver, visited):
    wait = WebDriverWait(driver, 10)  # Adjust the timeout as needed

    for i, xpath in enumerate(xpaths_options_list):
        if visited[i] == 0:
            try:
                element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                element.click()
                visited[i] = 1
            except (TimeoutException, NoSuchElementException):
                print(f"Element not interactable or not found: {xpath}")

    for i, (xpath, text) in enumerate(xpaths_text_list.items(), start=len(xpaths_options_list)):
        if visited[i] == 0:
            try:
                input_element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                input_element.clear()
                input_element.send_keys(text)
                visited[i] = 1
            except (TimeoutException, NoSuchElementException):
                print(f"Element not interactable or not found: {xpath}")

def click(xpaths_options_list, xpaths_text_list, form_url):
    visited = [0] * (len(xpaths_options_list) + len(xpaths_text_list))
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(form_url)
    time.sleep(1)
    visible_html = driver.execute_script("return document.body.innerHTML;")
    for i in range(6):
        driver.execute_script("window.scrollBy(0, 180);")
        click_all_visible_elements(xpaths_options_list, xpaths_text_list, driver, visited)
    submit_button_xpath = "//span[text()='Submit']"  # Update this XPath as needed
    
    try:
        # Wait for the submit button to be clickable
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, submit_button_xpath))
        )
        # Click the submit button
        submit_button.click()
        print("Form submitted successfully.")
    except TimeoutException:
        print("Submit button not found or not clickable.")
    except NoSuchElementException:
        print("Submit button not found.")

