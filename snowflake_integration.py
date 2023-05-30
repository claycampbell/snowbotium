import streamlit as st
import os
import snowflake.connector
snowflake_connection = os.getenv('SNOWFLAKE_CONNECTION')
# Snowflake connection parameters
snowflake_user = os.getenv('SNOWFLAKE_USER')
snowflake_password = os.getenv('SNOWFLAKE_PASSWORD')
snowflake_account = os.getenv('SNOWFLAKE_ACCOUNT')
snowflake_database = os.getenv('SNOWFLAKE_DATABASE')
snowflake_schema = os.getenv('SNOWFLAKE_SCHEMA')
snowflake_table_files = os.getenv('SNOWFLAKE_TABLE_FILES')
snowflake_table_responses = os.getenv('SNOWFLAKE_TABLE_RESPONSES')

# Establish Snowflake connection
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
    CREATE TABLE IF NOT EXISTS {snowflake_table_files} (
        id STRING,
        filename STRING,
        filedata VARIANT
    )
""")

cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {snowflake_table_responses} (
        id STRING,
        prompt STRING,
        response STRING
    )
""")

# Function to insert file data into Snowflake
def insert_file_data(file_id, filename, file_data):
    cursor.execute(f"""
        INSERT INTO {snowflake_table_files} (id, filename, filedata)
        VALUES ('{file_id}', '{filename}', PARSE_JSON('{file_data}'))
    """)
    conn.commit()

# Function to insert prompt-response data into Snowflake
def insert_prompt_response(prompt_id, prompt, response):
    cursor.execute(f"""
        INSERT INTO {snowflake_table_responses} (id, prompt, response)
        VALUES ('{prompt_id}', '{prompt}', '{response}')
    """)
    conn.commit()

# Snowbotium application code
def main():
    st.title("Snowbotium")

    # File upload
    uploaded_file = st.file_uploader("Choose a file", type=["pdf"])

    if uploaded_file is not None:
        file_id = st.session_state.id_counter  # Generate a unique ID for the file
        file_data = uploaded_file.getvalue().decode("utf-8")

        # Insert file data into Snowflake
        insert_file_data(file_id, uploaded_file.name, file_data)

        # Increment the ID counter
        st.session_state.id_counter += 1

        st.success("File uploaded and stored in Snowflake!")

    # Prompt and response
    prompt = st.text_input("Enter a prompt")
    if st.button("Generate Response"):
        response = generate_response(prompt)

        # Insert prompt-response data into Snowflake
        insert_prompt_response(st.session_state.id_counter, prompt, response)

        # Increment the ID counter
        st.session_state.id_counter += 1

        st.write(f"Response: {response}")

# Run the Snowbotium application
if __name__ == "__main__":
    if 'id_counter' not in st.session_state:
        st.session_state.id_counter = 1

    main()
