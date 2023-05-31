import streamlit as st
import openai
import os
import PyPDF2
import snowflake.connector
from langchain.agents import initialize_agent
from langchain.agents import Tool
from langchain.tools import BaseTool, DuckDuckGoSearchRun
from langchain.utilities import PythonREPL
from langchain.utilities import WikipediaAPIWrapper
from langchain.tools.ddg_search.tool import DuckDuckGoSearchRun
from FreeLLM import ChatGPTAPI

# Get the OpenAI API key from environment variables
api_key = os.getenv('OPENAI_API_KEY')
openai.api_key = api_key

# Snowflake connection parameters
snowflake_user = st.secrets["snowflake"]["user"]
snowflake_password = st.secrets["snowflake"]["password"]
snowflake_account = st.secrets["snowflake"]["account"]
snowflake_database = st.secrets["snowflake"]["database"]
snowflake_schema = st.secrets["snowflake"]["schema"]
snowbotium_table_files = "snowbotium_files"
snowbotium_table_responses = "snowbotium_responses"

# Initialize Snowflake connection
conn = snowflake.connector.connect(
    user=snowflake_user,
    password=snowflake_password,
    account=snowflake_account,
    warehouse='COMPUTE_WH',
    database=snowflake_database,
    schema=snowflake_schema
)

# Create Snowflake cursor
cursor = conn.cursor()

# Create Snowflake tables if they don't exist
cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {snowbotium_table_files} (
        id STRING,
        filename STRING,
        filedata VARCHAR
    )
""")

cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {snowbotium_table_responses} (
        id STRING,
        prompt STRING,
        response STRING
    )
""")

# Function to insert file data into Snowflake
def insert_file_data(file_id, filename, file_data):
    cursor.execute(f"""
        INSERT INTO {snowbotium_table_files} (id, filename, filedata)
        VALUES (%s, %s, %s)
    """, (file_id, filename, file_data))
    conn.commit()

# Function to insert prompt-response data into Snowflake
def insert_prompt_response(prompt_id, prompt, response):
    cursor.execute(f"""
        INSERT INTO {snowbotium_table_responses} (id, prompt, response)
        VALUES (%s, %s, %s)
    """, (prompt_id, prompt, response))
    conn.commit()

# Define the conversation with the model
def generate_responses(file_content, user_role):
    conversation = [
        {"role": "system", "content": "You are a technical business analyst."},
        {"role": "user", "content": "Here is a PDF document. Can you analyze it and provide information based on its content?"},
        {"role": "assistant", "content": file_content},
        {"role": "user", "content": user_role}
    ]

    # Call OpenAI Chat Completion API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation,
    )

    # Extract the responses from the model's output
    responses = []
    for choice in response.choices:
        response_text = choice.message.content
        responses.append(response_text)
    return responses

# Snowflake connector class
class SnowflakeConnector:
    def fetch_responses(self):
        # Retrieve the stored responses from Snowflake
        cursor.execute(f"SELECT response FROM {snowbotium_table_responses}")
        rows = cursor.fetchall()
        responses = [row[0] for row in rows]
        return responses

def show_home():
    st.title(":snowflake: Snowbotium")
    st.markdown("Accelerate Your Data Migration Project")
    st.markdown("Welcome to Snowbotium! This app helps you analyze PDF documents and generate insights based on their content. To get started, follow these steps:")
    st.markdown("- On the sidebar, upload a PDF file using the 'Upload PDF' section.")
    st.markdown("- Once the PDF file is uploaded, you can choose from various options to generate ideas, explain customer benefits, estimate effort and risks, and create a project plan based on the document's content.")
    st.markdown("- To keep up with the latest updates please view the Changelog page.")

def show_changelog():
    st.title("Changelog")

    st.subheader("Version 1.0")
    st.markdown("- Initial release of Snowbotium.")

    st.markdown("Highlights")
    st.markdown("🔌 Initial release of Snowbotium.")

    st.markdown("Notable Changes")
    st.markdown("🐼 Added PDF upload functionality, allowing users to upload PDF documents for analysis.")
    st.markdown("🍔 Implemented idea generation, benefit explanation, effort estimation, and project plan creation features.")
    st.markdown("🪵 Users can generate ideas for user stories, explain customer benefits, estimate effort and identify risks, and create a project plan based on the content of the uploaded document.")

    st.markdown("Other Changes")
    st.markdown("🔏 Integrated Snowflake database for storing file data and prompt-response information.")
    st.markdown("🤖 Users can view previously generated responses from Snowflake, providing a history of generated insights.")

    st.subheader("Version 1.1")
    st.markdown("🎨 Improved user interface with updated styling for a more intuitive and visually appealing experience.")
    st.markdown("⚡ Enhanced performance and stability, ensuring smooth execution of analysis and generation processes.")

    st.markdown("Highlights")
    st.markdown("🔌 Improved user interface with updated styling.")
    st.markdown("🚀 Enhanced performance and stability.")

    st.markdown("Notable Changes")
    st.markdown("📱 Improved responsiveness of the application for different screen sizes.")
    st.markdown("🛠 Optimized backend algorithms for faster generation of insights.")

    st.markdown("Other Changes")
    st.markdown("🔧 Fixed minor bugs and improved error handling.")
    st.markdown("🌈 Added new visualizations for better data representation.")

def show_aiagent():
    from langchain.prompts.chat import (
        SystemMessagePromptTemplate,
        HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    BaseMessage,
)
import os
import json
from pathlib import Path
from json import JSONDecodeError
from langchain.llms.base import LLM
from typing import Optional, List, Mapping, Any
from FreeLLM import HuggingChatAPI  # FREE HUGGINGCHAT API
from FreeLLM import ChatGPTAPI  # FREE CHATGPT API
from FreeLLM import BingChatAPI  # FREE BINGCHAT API
import streamlit as st
from streamlit_chat_media import message
import os

st.set_page_config(
    page_title="FREE AUTOGPT 🚀 by Intelligenza Artificiale Italia",
    page_icon="🚀",
    layout="wide",
    menu_items={
        "Get help": "https://www.intelligenzaartificialeitalia.net/",
        "Report a bug": "mailto:servizi@intelligenzaartificialeitalia.net",
        "About": "# *🚀  FREE AUTOGPT  🚀* ",
    },
)


st.markdown(
    "<style> iframe > div {    text-align: left;} </style>", unsafe_allow_html=True
)


class CAMELAgent:
    def __init__(
        self,
        system_message: SystemMessage,
        model: None,
    ) -> None:
        self.system_message = system_message.content
        self.model = model
        self.init_messages()

    def reset(self) -> None:
        self.init_messages()
        return self.stored_messages

    def init_messages(self) -> None:
        self.stored_messages = [self.system_message]

    def update_messages(self, message: BaseMessage) -> List[BaseMessage]:
        self.stored_messages.append(message)
        return self.stored_messages

    def step(
        self,
        input_message: HumanMessage,
    ) -> AIMessage:
        messages = self.update_messages(input_message)
        output_message = self.model(str(input_message.content))
        self.update_messages(output_message)
        print(f"AI Assistant:\n\n{output_message}\n\n")
        return output_message


col1, col2 = st.columns(2)
assistant_role_name = col1.text_input("Assistant Role Name", "Python Programmer")
user_role_name = col2.text_input("User Role Name", "Stock Trader")
task = st.text_area("Task", "Develop a trading bot for the stock market")
word_limit = st.number_input("Word Limit", 10, 1500, 50)

if not os.path.exists("cookiesHuggingChat.json"):
    raise ValueError(
        "File 'cookiesHuggingChat.json' not found! Create it and put your cookies in there in the JSON format."
    )
cookie_path = Path() / "cookiesHuggingChat.json"
with open("cookiesHuggingChat.json", "r") as file:
    try:
        file_json = json.loads(file.read())
    except JSONDecodeError:
        raise ValueError(
            "You did not put your cookies inside 'cookiesHuggingChat.json'! You can find the simple guide to get the cookie file here: https://github.com/IntelligenzaArtificiale/Free-Auto-GPT"
        )  
llm = HuggingChatAPI.HuggingChat(cookiepath = str(cookie_path))


if st.button("Start Autonomus AI AGENT"):
    task_specifier_sys_msg = SystemMessage(content="You can make a task more specific.")
    task_specifier_prompt = """Here is a task that {assistant_role_name} will help {user_role_name} to complete: {task}.
    Please make it more specific. Be creative and imaginative.
    Please reply with the specified task in {word_limit} words or less. Do not add anything else."""
    task_specifier_template = HumanMessagePromptTemplate.from_template(
        template=task_specifier_prompt
    )

    task_specify_agent = CAMELAgent(
        task_specifier_sys_msg, llm
    )
    task_specifier_msg = task_specifier_template.format_messages(
        assistant_role_name=assistant_role_name,
        user_role_name=user_role_name,
        task=task,
        word_limit=word_limit,
    )[0]

    specified_task_msg = task_specify_agent.step(task_specifier_msg)

    print(f"Specified task: {specified_task_msg}")
    message(
        f"Specified task: {specified_task_msg}",
        allow_html=True,
        key="specified_task",
        avatar_style="adventurer",
    )

    specified_task = specified_task_msg

    # messages.py
    from langchain.prompts.chat import (
        SystemMessagePromptTemplate,
        HumanMessagePromptTemplate,
    )

    assistant_inception_prompt = """Never forget you are a {assistant_role_name} and I am a {user_role_name}. Never flip roles! Never instruct me!
    We share a common interest in collaborating to successfully complete a task.
    You must help me to complete the task.
    Here is the task: {task}. Never forget our task and to focus only to complete the task do not add anything else!
    I must instruct you based on your expertise and my needs to complete the task.

    I must give you one instruction at a time.
    It is important that when the . "{task}" is completed, you need to tell {user_role_name} that the task has completed and to stop!
    You must write a specific solution that appropriately completes the requested instruction.
    Do not add anything else other than your solution to my instruction.
    You are never supposed to ask me any questions you only answer questions.
    REMEMBER NEVER INSTRUCT ME! 
    Your solution must be declarative sentences and simple present tense.
    Unless I say the task is completed, you should always start with:

    Solution: <YOUR_SOLUTION>

    <YOUR_SOLUTION> should be specific and provide preferable implementations and examples for task-solving.
    Always end <YOUR_SOLUTION> with: Next request."""

    user_inception_prompt = """Never forget you are a {user_role_name} and I am a {assistant_role_name}. Never flip roles! You will always instruct me.
    We share a common interest in collaborating to successfully complete a task.
    I must help you to complete the task.
    Here is the task: {task}. Never forget our task!
    You must instruct me based on my expertise and your needs to complete the task ONLY in the following two ways:

    1. Instruct with a necessary input:
    Instruction: <YOUR_INSTRUCTION>
    Input: <YOUR_INPUT>

    2. Instruct without any input:
    Instruction: <YOUR_INSTRUCTION>
    Input: None

    The "Instruction" describes a task or question. The paired "Input" provides further context or information for the requested "Instruction".

    You must give me one instruction at a time.
    I must write a response that appropriately completes the requested instruction.
    I must decline your instruction honestly if I cannot perform the instruction due to physical, moral, legal reasons or my capability and explain the reasons.
    You should instruct me not ask me questions.
    Now you must start to instruct me using the two ways described above.
    Do not add anything else other than your instruction and the optional corresponding input!
    Keep giving me instructions and necessary inputs until you think the task is completed.
    It's Important wich when the task . "{task}" is completed, you must only reply with a single word <CAMEL_TASK_DONE>.
    Never say <CAMEL_TASK_DONE> unless my responses have solved your task!
    It's Important wich when the task . "{task}" is completed, you must only reply with a single word <CAMEL_TASK_DONE>"""

    def get_sys_msgs(assistant_role_name: str, user_role_name: str, task: str):
        assistant_sys_template = SystemMessagePromptTemplate.from_template(
            template=assistant_inception_prompt
        )
        assistant_sys_msg = assistant_sys_template.format_messages(
            assistant_role_name=assistant_role_name,
            user_role_name=user_role_name,
            task=task,
        )[0]

        user_sys_template = SystemMessagePromptTemplate.from_template(
            template=user_inception_prompt
        )
        user_sys_msg = user_sys_template.format_messages(
            assistant_role_name=assistant_role_name,
            user_role_name=user_role_name,
            task=task,
        )[0]

        return assistant_sys_msg, user_sys_msg

    # define the role system messages
    assistant_sys_msg, user_sys_msg = get_sys_msgs(
        assistant_role_name, user_role_name, specified_task
    )

    # AI ASSISTANT setup                           |-> add the agent LLM MODEL HERE <-|
    assistant_agent = CAMELAgent(assistant_sys_msg, llm)

    # AI USER setup                      |-> add the agent LLM MODEL HERE <-|
    user_agent = CAMELAgent(user_sys_msg, llm)

    # Reset agents
    assistant_agent.reset()
    user_agent.reset()

    # Initialize chats
    assistant_msg = HumanMessage(
        content=(
            f"{user_sys_msg}. "
            "Now start to give me introductions one by one. "
            "Only reply with Instruction and Input."
        )
    )

    user_msg = HumanMessage(content=f"{assistant_sys_msg.content}")
    user_msg = assistant_agent.step(user_msg)
    message(
        f"AI Assistant ({assistant_role_name}):\n\n{user_msg}\n\n",
        is_user=False,
        allow_html=True,
        key="0_assistant",
        avatar_style="pixel-art",
    )
    print(f"Original task prompt:\n{task}\n")
    print(f"Specified task prompt:\n{specified_task}\n")

    chat_turn_limit, n = 30, 0
    while n < chat_turn_limit:
        n += 1
        user_ai_msg = user_agent.step(assistant_msg)
        user_msg = HumanMessage(content=user_ai_msg)
        # print(f"AI User ({user_role_name}):\n\n{user_msg}\n\n")
        message(
            f"AI User ({user_role_name}):\n\n{user_msg.content}\n\n",
            is_user=True,
            allow_html=True,
            key=str(n) + "_user",
        )

        assistant_ai_msg = assistant_agent.step(user_msg)
        assistant_msg = HumanMessage(content=assistant_ai_msg)
        # print(f"AI Assistant ({assistant_role_name}):\n\n{assistant_msg}\n\n")
        message(
            f"AI Assistant ({assistant_role_name}):\n\n{assistant_msg.content}\n\n",
            is_user=False,
            allow_html=True,
            key=str(n) + "_assistant",
            avatar_style="pixel-art",
        )
        if (
            "<CAMEL_TASK_DONE>" in user_msg.content
            or "task  completed" in user_msg.content
        ):
            message("Task completed!", allow_html=True, key="task_done")
            break
        if "Error" in user_msg.content:
            message("Task failed!", allow_html=True, key="task_failed")
            break


def main():
    # Set page title and favicon
    st.set_page_config(page_title="Snowbotium", page_icon=":snowflake:")

    # Display the menu of links
    st.sidebar.title("Navigation")
    menu_options = ["Home"]
    menu_options = ["aiagent"]

    for option in menu_options:
        st.sidebar.markdown(f"- [{option}](#{option.replace(' ', '-').lower()})")

    st.sidebar.markdown("---")

    # Upload a PDF file
    st.sidebar.title("Upload PDF")
    uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        # Read the uploaded PDF file
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        file_content = ""
        for page in pdf_reader.pages:
            file_content += page.extract_text()

        # Store file content in Snowflake
        insert_file_data(str(uploaded_file.name), uploaded_file.name, file_content)

        # Generate Ideas for User Stories
        if st.button("Generate Ideas for User Stories", key="generate-ideas"):
            with st.spinner("Generating ideas..."):
                responses = generate_responses(file_content, "Generate ideas for user stories.")
            st.success("Ideas Generated!")

            # Store responses in Snowflake
            for response in responses:
                insert_prompt_response(str(uploaded_file.name), "Generate ideas for user stories.", response)

            # Display Responses
            st.subheader("User Story Ideas:")
            for index, response in enumerate(responses, start=1):
                st.write(f"Idea {index}: {response}")

        # Explain Customer Benefits
        if st.button("Explain Customer Benefits", key="explain-benefits"):
            with st.spinner("Explaining Benefits..."):
                responses = generate_responses(file_content, "What are the main benefits of this project for the customer?")
            st.success("Benefits Explained!")

            # Store responses in Snowflake
            for response in responses:
                insert_prompt_response(str(uploaded_file.name), "What are the main benefits of this project for the customer?", response)

            # Display Responses
            st.subheader("Customer Benefits:")
            for index, response in enumerate(responses, start=1):
                st.write(f"Response {index}: {response}")

        # Estimate Effort and Identify Risks
        if st.button("Estimate Effort and Identify Risks", key="estimate-effort"):
            with st.spinner("Estimating effort and identifying risks..."):
                responses = generate_responses(file_content, "What are the main tasks required to complete this project?")
            st.success("Effort Estimated and Risks Identified!")

            # Store responses in Snowflake
            for response in responses:
                insert_prompt_response(str(uploaded_file.name), "What are the main tasks required to complete this project?", response)

            # Display Responses
            st.subheader("Effort Estimate and Risks:")
            for index, response in enumerate(responses, start=1):
                st.write(f"Response {index}: {response}")

        # Create Project Plan
        if st.button("Create Project Plan", key="create-plan"):
            with st.spinner("Creating project plan..."):
                responses = generate_responses(file_content, "Create a project plan based on the document's content.")
            st.success("Project Plan Created!")

            # Store responses in Snowflake
            for response in responses:
                insert_prompt_response(str(uploaded_file.name), "Create a project plan based on the document's content.", response)

            # Display Responses
            st.subheader("Project Plan:")
            for index, response in enumerate(responses, start=1):
                st.write(f"Response {index}: {response}")

        # Initialize Snowflake connector
        snowflake_connector = SnowflakeConnector()

        # View Previously Generated Responses
        with st.beta_expander("View Previously Generated Responses"):
            with st.spinner("Loading responses..."):
                # Retrieve the stored responses from Snowflake
                responses = snowflake_connector.fetch_responses()

            # Display the responses
            if responses:
                st.subheader("Previously Generated Responses:")
                for index, response in enumerate(responses, start=1):
                    st.write(f"Response {index}: {response}")
            else:
                st.info("No responses found.")

    # Handle the selected option
    if st.sidebar.button("Changelog"):
        show_changelog()
    else:
        # Handle the Home option
        show_home()

if __name__ == "__main__":
    main()

