import streamlit as st
import openai
import os
import PyPDF2
from snowflake_integration import SnowflakeConnector

# Get the OpenAI API key from environment variables
api_key = os.getenv('OPENAI_API_KEY')
openai.api_key = api_key

# Initialize Snowflake connector
snowflake_connector = SnowflakeConnector()

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


def main():
    # Set page title and favicon
    st.set_page_config(page_title="Snowbotium", page_icon=":snowflake:")

    # Header
    st.title(":snowflake: Snowbotium")
    st.markdown("Accelerate Your Data Migration Project")

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
        snowflake_connector.insert_file_content(file_content)

        # Generate Ideas for User Stories
        if st.button("Generate Ideas for User Stories"):
            with st.spinner("Generating ideas..."):
                responses = generate_responses(file_content, "Generate ideas for user stories.")
            st.success("Ideas Generated!")

            # Store responses in Snowflake
            snowflake_connector.insert_responses(responses)

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
            snowflake_connector.insert_responses(responses)

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
            snowflake_connector.insert_responses(responses)

            # Display Responses
            st.subheader("Effort and Risks:")
            for index, response in enumerate(responses, start=1):
                st.write(f"Response {index}: {response}")

        # Create Project Plan
        if st.button("Create Project Plan"):
            with st.spinner("Creating project plan..."):
                responses = generate_responses(file_content, "Create a project plan for this project.")
            st.success("Project Plan Created!")

            # Store responses in Snowflake
            snowflake_connector.insert_responses(responses)

            # Display Responses
            st.subheader("Project Plan:")
            for index, response in enumerate(responses, start=1):
                st.write(f"Response {index}: {response}")


if __name__ == "__main__":
    main()
      

