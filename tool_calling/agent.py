# imports and environment setup
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_react_agent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os 
from langchain_google_genai import ChatGoogleGenerativeAI
import json
from langchain_mistralai import ChatMistralAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv
# New import for processing HTML
from process_html import process_form_answers 
import re
import time
# Agent initialization and form filling logic
load_dotenv()

def initialise_agent(prompt):
   
    try:
        with open("xpaths.json", "r") as json_file:
            json_object = json.load(json_file)
    except FileNotFoundError:
        print("Error: xpaths.json file not found.")
        return None
    except json.JSONDecodeError:
        print("Error: Invalid JSON in xpaths.json file.")
        return None

    @tool
    def fill_form(json_text):
        """  fill the form based on the xpaths of elements you have given it.
         The input to the tool 
         Use this tool with json like "{{"clickable_options": ["xpath of option to be clicked","xpath of option to be clicked",..],
                                    "fill_text":[ ["xpath of text field1","text to be filled in field1"],
                                                    ["xpath of text field2","text to be filled in field2"],.. ]
                                    }} when you need to fill the form'
        """
        json_pattern = re.compile(r'```\s*(.*?)\s*```', re.DOTALL)
        json_match = json_pattern.search(json_text) 
        json_text=json_match.group(1) 
        json_text=json_text.replace("json","")
        json_object=json.loads(json_text)
        print(json_object)
        def click_all_visible_elements(xpaths_options_list,xpaths_text_list,driver,visited):
            
            #enumerate the xpaths_options_list
            for i,xpath in enumerate(xpaths_options_list):
                try:
                    # driver.execute_script("window.scrollBy(0, 300);")
                    if visited[i]==1:
                        continue
                    element = WebDriverWait(driver, 1).until(
                        EC.element_to_be_clickable((By.XPATH, xpath))
                    )
                    element.click()
                    time.sleep(0.5)
                    visited[i]=1
                except (TimeoutException, NoSuchElementException) as e:
                    visited[i]=0
                    # print(f"Element not found or not clickable: {xpath}")

            # Fill the text boxes with content
            #enumerate the xpaths_text_list
            #change the code if xpaths_text_list is a list of list 
            for i, (xpath, text) in enumerate(xpaths_text_list):
                try:
                    # driver.execute_script("window.scrollBy(0, 300);")
                    if visited[len(xpaths_options_list)+i]==1:
                        continue
                    input_element = WebDriverWait(driver, 1).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    input_element.send_keys(text)
                    time.sleep(0.5)
                    visited[len(xpaths_options_list)+i]=1
                except (TimeoutException, NoSuchElementException) as e:
                    visited[len(xpaths_options_list)+i]=0
                    # print(f"Element not found or not interactable: {xpath}")

        def click(xpaths_options_list,xpaths_text_list):
            visited=[0]*(len(xpaths_options_list)+len(xpaths_text_list))
            form_url='https://docs.google.com/forms/d/e/1FAIpQLSd9gli7KqnYFNkrc_PWNxvmhi7ZJz2jPp0qTsceqT7lkIBo2Q/viewform'
            driver = webdriver.Chrome()
            driver.maximize_window()
            driver.get(form_url)
            time.sleep(1)
            # visible_html = driver.execute_script("return document.body.innerHTML;")
            for i in range(4):
                driver.execute_script("window.scrollBy(0, 180);")
                click_all_visible_elements(xpaths_options_list,xpaths_text_list,driver,visited)
            time.sleep(2)

            # Submit the form after filling
            submit_button_xpath = "//span[text()='Submit']" 
            try:
                submit_button = WebDriverWait(driver, 1).until(
                    EC.element_to_be_clickable((By.XPATH, submit_button_xpath))
                )
                submit_button.click()
                time.sleep(2)  # Wait for the submission to process
            except (TimeoutException, NoSuchElementException) as e:
                print("Error: Submit button not found or not clickable.")

            driver.quit()
            response=""
            exit_flag=1
            for i in range(len(visited)):
                exit_flag&=visited[i]
                if visited[i]==0:
                    if i<len(xpaths_options_list):
                        response+=f"Element with xpath {xpaths_options_list[i]} not found or not clickable. Try again with a new xpath\n"
                    else:
                        response+=f"Element with xpath {xpaths_text_list[i-len(xpaths_options_list)][0]} not found or not filled . Try again with a new xpath\n"
                else:
                    if i<len(xpaths_options_list):
                        response+=f"Element with xpath {xpaths_options_list[i]} found and clicked\n"
                    else:
                        response+=f"Element with xpath {xpaths_text_list[i-len(xpaths_options_list)][0]} found and filled with {xpaths_text_list[i-len(xpaths_options_list)][1]} .  \n"

            print(response)
            return response

        xpaths_options_list=json_object['clickable_options']
        xpaths_text_list=json_object['fill_text']
        # print(xpaths_options_list,xpaths_text_list)
        # print(type(xpaths_options_list),type(xpaths_text_list))
        xpaths_options_list=list(xpaths_options_list) 
        xpaths_text_list=list(xpaths_text_list)
        # print(xpaths_options_list,xpaths_text_list)
        # print(type(xpaths_options_list),type(xpaths_text_list))

        response=click(xpaths_options_list,xpaths_text_list)

        return response


    tools=[fill_form]
    # llm=ChatOpenAI(model='gpt-4o-mini')
    # llm=ChatGroq(model='llama-3.1-70b-versatile')

    # agent = create_react_agent(llm, tools, prompt)
    llm = ChatMistralAI(model="mistral-large-latest")

    agent=create_react_agent(llm,tools,prompt)

    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False,return_intermediate_steps=True,handle_parsing_errors=True)
    return agent_executor


def main(form_url, user_info):
        answers = process_form_answers(form_url, user_info)  # Cleaned up to use the new function

        prompt=PromptTemplate.from_template(""" 
        You are a helpful assistant that can fill google forms.
        -You need to fill the text in fields,click options,etc.  
        The options/fields that of form needs to be filled/clicked  are : {response} \n
        It contains html and also xpaths(which i m not sure about) of the options/fields of the options/fields,text of the options/fields.

        ----------------------------------------
        You have access to the following tools:

        {tools}
        ---
        Tool names:
        {tool_names}
        ------------------------------------------------------


        You can fill the form by using the tool fill_form which can fill the form based on the xpaths of elements you have given it.


        -the input of fill_form is a json with keys "clickable_options" and "fill_text"
        -the value of "clickable_options" is a list of xpaths of clickable options
        -the value of "fill_text" is a list of xpaths of text fields and the text to be filled in them...

        thus input is a json of form:
         like ``` {{"clickable_options": ["xpath of option to be clicked","xpath of option to be clicked",..],
                                        "fill_text":[ ["xpath of text field1","text to be filled in field1"],
                                                        ["xpath of text field2","text to be filled in field2"],.. ]
                                        }} .   ```                                


        The response of the tool is a string which tells about the status of the form filling.
        The response consists if the element is not found/clickable,then it will say that element not found/clickable 
        then u need to change the xpath and try again.   
        If the element is found/clickable then it will say that element found/clickable thus it was correct so in 
        next iteration keep the xpath same and change the other xpaths that had failed
        If in response it mentions all elements were clicked/filled you need to exit..


        Based on the {response}, perform the following tasks: 

        Identify all interactive elements (buttons, input fields, etc.) that need to be clicked or filled.
        Generate XPath selectors for each identified element.
        Use the 'fill_form' action to interact with the elements.
        For each element, pass its XPath as input to the 'fill_form' action.
        Analyze the response from 'fill_form':

        If an element is not found or not clickable, generate an alternative XPath based on the HTML structure (i.e from {response} \n)
        Retry the 'fill_form' action with the new XPath.


        In each iteration, attempt to interact with ALL elements, including those successfully handled in previous iterations.

        Do not change XPaths for previously successful elements.


        Repeat steps 3-6 up to 4 times or until all elements are successfully interacted with.
        After each iteration, provide a status update including:

        Elements successfully interacted with
        Elements that failed and their current XPaths
        Number of iterations completed


        If all elements are successfully handled, or after 4 iterations, provide a final report summarizing the results."



        Use the following format to answer:

        Thought :Identify what all options u need to click/fill and xpaths of those element 
        or else if u have filled the form then return "filled the whole form".

        Action : fill_form or none
        Action Input : the input to the tool fill_form with json object with keys "clickable_options" and "fill_text"

        Observation: analyse the response of the tool fill_form.


        (this Thought/Action/Action Input/Observation can repeat upto maximum of 4 times,
        if u have filled the form then exit this loop)


        Final return: filled the whole form o
        Begin!

        Thought: {agent_scratchpad}
        """
        )

        agent=initialise_agent(prompt)
        result=agent.invoke({"response": answers})
        print(result)

main("https://docs.google.com/forms/d/e/1FAIpQLSd9gli7KqnYFNkrc_PWNxvmhi7ZJz2jPp0qTsceqT7lkIBo2Q/viewform", "Hey, I am an existing customer, and I want to order pens and notebooks of red and blue colors. Quantity of the items should be 4. As per details about me, I’m Kavan, and I’m available at 9548565487 / kavan@gmail.com. Preferred mode of communication is either phone or email. Thanks!")