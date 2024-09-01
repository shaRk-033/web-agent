import json
import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_answers(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data  # Return the entire data structure
    except FileNotFoundError:
        logger.error(f"Answers file not found: {file_path}")
        raise
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in answers file: {file_path}")
        raise

def click_element(driver, xpath):
    try:
        element = WebDriverWait(driver, 1).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        element.click()
        logger.info(f"Successfully clicked element with XPath: {xpath}")
        return True
    except (TimeoutException, NoSuchElementException) as e:
        logger.warning(f"Element not found or not clickable: {xpath}")
        return False

def fill_text_input(driver, xpath, text):
    try:
        input_element = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        input_element.clear()
        input_element.send_keys(text)
        logger.info(f"Successfully filled text input with XPath: {xpath}")
        return True
    except (TimeoutException, NoSuchElementException) as e:
        logger.warning(f"Element not found or not interactable: {xpath}")
        return False

def fill_form(driver, answers):
    # Click on option elements
    for xpath in answers['xpaths_options_list']:
        click_element(driver, xpath)
        time.sleep(0.5)
    
    # Fill text inputs
    for xpath, text in answers['xpaths_text_list'].items():
        fill_text_input(driver, xpath, text)
        time.sleep(0.5)

    logger.info("All form elements processed")

def main():
    driver = webdriver.Chrome()
    driver.maximize_window()
    try:
        answers = load_answers('answers.json')
        logger.info("Answers loaded successfully")

        form_url = "https://docs.google.com/forms/d/e/1FAIpQLSd9gli7KqnYFNkrc_PWNxvmhi7ZJz2jPp0qTsceqT7lkIBo2Q/viewform"
        driver.get(form_url)
        logger.info(f"Navigated to form URL: {form_url}")

        # Wait for the form to load
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//form"))
        )

        fill_form(driver, answers)

        submit_button_xpath = "//div[@role='button' and contains(., 'Submit')]"
        if click_element(driver, submit_button_xpath):
            logger.info("Clicked submit button")

            confirmation_xpath = "//div[contains(text(), 'Your response has been recorded')]"
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, confirmation_xpath))
            )
            logger.info("Submission confirmed")
        else:
            logger.error("Failed to click submit button")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        driver.save_screenshot("error_screenshot_final.png")
    finally:
        time.sleep(10)
        driver.quit()
        logger.info("Browser closed")

if __name__ == "__main__":
    main()
