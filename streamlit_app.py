import streamlit as st
import openai
import os
import PyPDF2
import snowflake.connector

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

def show_changelog():
    st.title("Changelog")
    st.subheader("Version 1.0")
    st.markdown("- Initial release of Snowbotium.")
    st.markdown("- Added PDF upload functionality.")
    st.markdown("- Implemented idea generation, benefit explanation, effort estimation, and project plan creation features.")
    st.markdown("- Added Changelog page.")

    st.subheader("Version 1.1")
    st.markdown("- Improved user interface with updated styling.")
    st.markdown("- Enhanced performance and stability.")
    st.markdown("- Fixed bugs and addressed user feedback.")

def main():
    # Set page title and favicon
    st.set_page_config(page_title="Snowbotium", page_icon=":snowflake:")

    # Display the menu of links
    st.sidebar.title("Navigation")
    menu_options = ["Home"]

    for option in menu_options:
        st.sidebar.markdown(f"- [{option}](#{option.replace(' ', '-').lower()})")

    st.sidebar.markdown("---")

    # Handle the selected option
    if st.sidebar.button("Changelog"):
        show_changelog()
    else:
        # Handle the Home option
        show_home()

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
        if st.button("Generate Ideas for User Stories"):
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
        if st.button("Explain Customer Benefits"):
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
        if st.button("Estimate Effort and Identify Risks"):
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
        if st.button("Create Project Plan"):
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
    if st.sidebar.button("View Previously Generated Responses"):
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


if __name__ == "__main__":
    main()

