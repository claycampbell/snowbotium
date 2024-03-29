import streamlit as st

# Set page title and favicon
st.set_page_config(page_title="Snowbotium", page_icon=":snowflake:")

# Display the menu of links
st.sidebar.title("Navigation")
menu_options = ["Home", "AI Agent"]

for option in menu_options:
    st.sidebar.markdown(f"- [{option}](#{option.replace(' ', '-').lower()})")

st.sidebar.markdown("---")

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
from FreeLLM import HuggingChatAPI 
# Hugging FACE
os.environ["HUGGINGFACE_TOKEN"] = "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"

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
def main():
  
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
    
# Instantiate a ChatGPT object with your token
    llm = HuggingChatAPI.HuggingChat() 

# or use Bing CHAT
# llm = BingChatAPI.BingChat(cookiepath="cookie_path")

# or use Google BArd CHAT
# llm=BardChatAPI.BardChat(cookie="cookie") 

# or use HuggingChatAPI if u dont have CHATGPT, BING or Google account
# llm = HuggingChatAPI.HuggingChat() 


# Define the tools
    wikipedia = WikipediaAPIWrapper()
    python_repl = PythonREPL()
    search = DuckDuckGoSearchRun()

    tools = [
        Tool(
            name = "python repl",
            func=python_repl.run,
            description="useful for when you need to use python to answer a question. You should input python code"
        )
    ]

    wikipedia_tool = Tool(
        name='wikipedia',
        func= wikipedia.run,
        description="Useful for when you need to look up a topic, country or person on wikipedia"
    )

    duckduckgo_tool = Tool(
        name='DuckDuckGo Search',
        func= search.run,
        description="Useful for when you need to do a search on the internet to find information that another tool can't find. be specific with your input."
    )

    tools.append(duckduckgo_tool)
    tools.append(wikipedia_tool)


#Create the Agent
    iteration = (int(input("Enter the number of iterations: ")) if input("Do you want to set the number of iterations? (y/n): ") == "y" else 3)

    zero_shot_agent = initialize_agent(
        agent="zero-shot-react-description", 
        tools=tools, 
        llm=llm,
        verbose=True,
        max_iterations=iteration,
    )

# Start your Custom Agent in loop
    print(">> STRAT CUSTOM AGENT")
    print("> Digit 'exit' for exit or 'your task or question' for start\n\n")
    prompt = input("(Enter your task or question) >> ")
    while prompt.toLowerCase() != "exit":
        zero_shot_agent.run(prompt)
        prompt = input("(Enter your task or question) >> ")
    

  
# Handle the selected option

if st.sidebar.button("AI Agent"):
    show_aiagent()
elif st.sidebar.button("Changelog"):
    show_changelog()
else:
    # Handle the Home option
    show_home()


if __name__ == "__main__":
    main()

