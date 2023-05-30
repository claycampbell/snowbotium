import streamlit as st
import snowflake.connector


# Snowflake connection parameters
snowflake_user = st.secrets["snowflake"]["user"]
snowflake_password = st.secrets["snowflake"]["password"]
snowflake_account = st.secrets["snowflake"]["account"]
snowflake_database = st.secrets["snowflake"]["database"]
snowflake_schema = st.secrets["snowflake"]["schema"]
snowflake_table_files = st.secrets["snowflake"]["table_files"]
snowflake_table_responses = st.secrets["snowflake"]["table_responses"]

# Establish Snowflake connection
conn = snowflake.connector.connect(
    user=st.secrets["snowflake_user"],
    password=st.secrets["snowflake_password"],
    account=st.secrets["snowflake_account"],
    warehouse='COMPUTE_WH',
    database=st.secrets["snowflake_database"],
    schema=st.secrets["snowflake_schema"]
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
