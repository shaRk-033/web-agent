# from get_html import get_html
# from process import process_html_to_json
# from find_answers import generate_selenium_script
# from selenium import webdriver

# # form_url = 'https://docs.google.com/forms/d/e/1FAIpQLSd9gli7KqnYFNkrc_PWNxvmhi7ZJz2jPp0qTsceqT7lkIBo2Q/viewform'
# user_input = """
#     Hey, I am an existing customer, and I want to order pens and notebooks of red and blue colors. 
#     Quantity of the items should be 4. As per details about me, I'm Kavan, and I'm available at 
#     9548565487 / kavan@gmail.com. Preferred mode of communication is either phone or email.
#     """
# get_html(form_url)

# process_html_to_json('visible_html_orders.html', 'results.json')
# generate_selenium_script('results.json', 'execution_script.py')

# from execution_script import fill

# fill(webdriver.Chrome(), form_url)