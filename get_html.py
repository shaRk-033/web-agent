from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException
import time

def get_html(form_url):
    try:
        driver = webdriver.Chrome()
        driver.get(form_url)
        time.sleep(1)
        visible_html = driver.execute_script("return document.body.innerHTML;")

        with open("visible_html_orders.html", "w") as f:
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