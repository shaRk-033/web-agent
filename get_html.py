from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException
import time

form_url = 'https://docs.google.com/forms/d/e/1FAIpQLSd9gli7KqnYFNkrc_PWNxvmhi7ZJz2jPp0qTsceqT7lkIBo2Q/viewform'

try:
    driver = webdriver.Chrome()
    driver.get(form_url)
    time.sleep(1)
    visible_html = driver.execute_script("return document.body.innerHTML;")

    with open("visible_html_orders.html", "w") as f:
        f.write(visible_html)

except WebDriverException as e:
    print(f"WebDriverException occurred: {e}")
except TimeoutException as e:
    print(f"TimeoutException occurred: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    driver.quit()