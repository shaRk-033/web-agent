# Tool Calling Documentation

## Overview
This documentation provides an in-depth overview of the tool calling system designed to automate the process of filling Google Forms using Selenium and various AI models. The system retrieves form data, processes it, and interacts with the form elements based on the provided user information.

## File Structure
The project consists of the following main files:

- `process_html.py`: Handles the processing of form answers and interaction with AI models.
- `agent.py`: Initializes the agent that fills the form based on the processed data.
- `utils.py`: Contains utility functions for HTML processing, file handling, and logging.

## Dependencies
The following libraries are required:
- `selenium`: For web automation.
- `langchain_openai`: For OpenAI model interactions.
- `langchain_google_genai`: For Google Generative AI interactions.
- `langchain_mistralai`: For Mistral AI interactions.
- `langchain_groq`: For Groq model interactions.
- `dotenv`: For environment variable management.
- `json`: For JSON handling.
- `re`: For regular expressions.
- `os`: For operating system interactions.

## Functionality

### 1. `process_form_answers(form_url, user_info)`
- **Description**: This function retrieves the HTML of a Google Form, generates prompts for AI models, and processes the responses to extract relevant data.
- **Parameters**:
  - `form_url`: The URL of the Google Form.
  - `user_info`: Information about the user filling the form.
- **Returns**: A JSON object containing the matched answers.

### 2. `initialise_agent(prompt)`
- **Description**: Initializes the agent that will fill the form based on the provided prompt.
- **Parameters**:
  - `prompt`: The prompt template for the agent.
- **Returns**: An `AgentExecutor` instance.

### 3. `main(form_url, user_info)`
- **Description**: The main entry point of the application that orchestrates the form filling process.
- **Parameters**:
  - `form_url`: The URL of the Google Form.
  - `user_info`: Information about the user filling the form.
- **Returns**: None (prints the result of the agent's actions).

### 4. Utility Functions in `utils.py`
- **`get_html(form_url)`**: Retrieves the HTML content of the specified form URL.
- **`read_html_file(file_path)`**: Reads the content of an HTML file.
- **`write_to_file(file_path, content, as_json=False)`**: Writes content to a specified file, optionally as JSON.
- **`extract_json_from_response(response)`**: Extracts JSON data from a response string.
- **`generate_prompt_gemini(visible_html)`**: Generates a prompt for the Gemini model based on the visible HTML.
- **`generate_prompt_to_answer(response, user_info)`**: Generates a prompt for the AI model to determine user answers based on the provided information.

## Logging
The system logs events such as clicks, scrolls, and form submissions to a JSON file (`events.json`) for tracking and debugging purposes.

## Usage
To run the tool, call the `main` function with the appropriate form URL and user information. Ensure that all dependencies are installed and the environment is set up correctly.

## Conclusion
This tool calling system automates the process of filling Google Forms using Langchain Agents, Tool Calling, and Selenium, providing a robust solution for form automation tasks.

## Langchain Agents and Tool Calling
### Overview
Langchain Agents are designed to facilitate the interaction between AI models and external tools, allowing for dynamic decision-making and task execution based on the model's responses. The tool calling functionality enables the agent to invoke specific actions or functions based on the context provided in the prompt.

### Key Components
1. **Agent Initialization**: The agent is initialized with a prompt that outlines its capabilities and the tools available for use.
2. **Tool Invocation**: The agent can call tools (functions) to perform specific tasks, such as filling out forms or processing data.
3. **Response Handling**: The agent analyzes the responses from the tools and can make decisions on subsequent actions based on the results.

### Example Workflow
1. **Prompt Generation**: The agent receives a prompt that describes the task (e.g., filling a form).
2. **Tool Execution**: The agent invokes the `fill_form` tool, passing the necessary parameters (e.g., xpaths of form elements).
3. **Response Analysis**: The agent evaluates the response from the tool to determine if the task was successful or if adjustments are needed.
4. **Iteration**: The agent can repeat the process, adjusting its approach based on previous outcomes, until the task is completed or a maximum number of attempts is reached.

This architecture allows for flexible and intelligent automation of tasks, leveraging the capabilities of AI models in conjunction with traditional programming functions.

