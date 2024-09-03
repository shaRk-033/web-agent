# Backend Documentation

## Overview
This backend is designed to process Google Forms using Selenium for web automation and LangChain for natural language processing. It extracts questions from a form, generates answers based on user information, and submits the form automatically.

---

## File Descriptions

1. **`process.py`**
   - **Purpose**: Main processing logic for handling Google Forms.
   - **Key Functions**:
     - `read_html_file(file_path)`: Reads the content of an HTML file.
     - `write_to_file(file_path, content, as_json=False)`: Writes content to a specified file, optionally in JSON format.
     - `extract_json_from_response(response)`: Extracts JSON data from a response string using regex.
     - `generate_prompt_gemini(visible_html)`: Creates a prompt for the Gemini model to extract questions from the HTML.
     - `generate_prompt_to_answer(response, user_info)`: Generates a prompt for the OpenAI model to determine answers based on user info.
     - `async def process_form(user_info, form_url)`: Main asynchronous function that orchestrates the form processing, including fetching HTML, generating prompts, and writing results.

2. **`utils.py`**
   - **Purpose**: Contains utility functions for interacting with the web form.
   - **Key Functions**:
     - `click_all_visible_elements(xpaths_options_list, xpaths_text_list, driver, visited)`: Clicks on all visible elements based on provided XPath lists and logs events.
     - `click(xpaths_options_list, xpaths_text_list, form_url)`: Manages the Selenium driver to open the form URL, scroll, and click elements.
     - `log_event(event)`: Logs events to a JSON file for tracking interactions.

3. **`main.py`**
   - **Purpose**: Entry point for the FastAPI application.
   - **Key Functions**:
     - `async def root()`: Returns a welcome message for the API.
     - `async def submit_form(data: FormData)`: Handles form submission requests, validates input, and calls the `process_form` function.

4. **`get_html.py`**
   - **Purpose**: Fetches the HTML content of a Google Form.
   - **Key Functions**:
     - `get_html(form_url)`: Uses Selenium to navigate to the form URL and retrieves the HTML content.

---

## Function Details

### `process.py`

- **`read_html_file(file_path)`**
  - **Parameters**: `file_path` (str): Path to the HTML file.
  - **Returns**: Content of the HTML file as a string.

- **`write_to_file(file_path, content, as_json=False)`**
  - **Parameters**: 
    - `file_path` (str): Path to the file where content will be written.
    - `content` (str or dict): Content to write.
    - `as_json` (bool): If True, writes content as JSON.
  - **Returns**: None.

- **`extract_json_from_response(response)`**
  - **Parameters**: `response` (str): Response string containing JSON.
  - **Returns**: Parsed JSON object or None if no JSON is found.

- **`generate_prompt_gemini(visible_html)`**
  - **Parameters**: `visible_html` (str): HTML content of the Google Form.
  - **Returns**: Formatted prompt string for the Gemini model.

- **`generate_prompt_to_answer(response, user_info)`**
  - **Parameters**: 
    - `response` (str): Response from the Gemini model.
    - `user_info` (str): Information provided by the user.
  - **Returns**: Formatted prompt string for the OpenAI model.

- **`async def process_form(user_info, form_url)`**
  - **Parameters**: 
    - `user_info` (str): User information for form filling.
    - `form_url` (str): URL of the Google Form.
  - **Returns**: None. Processes the form and writes results to files.

### `utils.py`

- **`click_all_visible_elements(xpaths_options_list, xpaths_text_list, driver, visited)`**
  - **Parameters**: 
    - `xpaths_options_list` (list): List of XPath strings for clickable options.
    - `xpaths_text_list` (dict): Dictionary of XPath strings for text inputs.
    - `driver` (webdriver): Selenium WebDriver instance.
    - `visited` (list): List tracking which elements have been interacted with.
  - **Returns**: None. Clicks elements and logs events.

- **`click(xpaths_options_list, xpaths_text_list, form_url)`**
  - **Parameters**: 
    - `xpaths_options_list` (list): List of XPath strings for clickable options.
    - `xpaths_text_list` (dict): Dictionary of XPath strings for text inputs.
    - `form_url` (str): URL of the Google Form.
  - **Returns**: None. Opens the form and interacts with elements.

- **`log_event(event)`**
  - **Parameters**: `event` (dict): Event data to log.
  - **Returns**: None. Appends event data to the events JSON file.

### `main.py`

- **`async def root()`**
  - **Returns**: JSON response with a welcome message.

- **`async def submit_form(data: FormData)`**
  - **Parameters**: `data` (FormData): Data model containing user info and form URL.
  - **Returns**: JSON response indicating success or failure.

### `get_html.py`

- **`get_html(form_url)`**
  - **Parameters**: `form_url` (str): URL of the Google Form.
  - **Returns**: HTML content of the form as a string or None if an error occurs.

---

## Usage
1. Start the FastAPI server by running `python main.py`.
2. Send a POST request to `/form` with JSON body containing `user_info` and `form_url`.
3. The backend will process the form, extract questions, generate answers, and submit the form automatically.