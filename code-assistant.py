# Code Assistant
# This application will help the user with 2 things. 
# 1. Generate a logical database design (coming soon)
# 2. Be a coding assistant to do the following : Generate flow diagram in mermaid script, generate documentation or perform conversion to a different programming language. 
# 3. Generate boilerplate code for Python by using the mermaid script uploaded as input in text file format.
# Idea is to use these to save some time doing these tasks and thus, productivity gain. 
# parag.jn@gmail.com
# December 2024

import streamlit as st
from openai_client import OpenAIClient

# Streamlit application setup
st.set_page_config(
    page_title="Open Ai - Code Helper with o1 Model",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'About': "# A Code Helper Tool!"},
)

# system variables
MODEL = 'o1-mini'

# Initialize OpenAI Client
openai_client_obj = OpenAIClient()
client = openai_client_obj.get_client()

def run_LLM(prompt, role="You are a helpful assistant"):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message

# Set the title of the application
st.title("A Coding Assistant")
st.write("---")

# Create a sidebar with a title
st.sidebar.title("Select Option")
st.sidebar.write("---")

# Add radio buttons to the sidebar
option = st.sidebar.radio(label="Select Option", options=['None', 'DB Generator', 'Code Assistant'])

# Logic for DB Generator
if option == 'DB Generator':
    col1, col2 = st.columns([3, 10], gap="small")
    with col1:
        db_name = st.text_input(label="Provide with database name", value="", max_chars=50)
    with col2:
        entities = st.text_area(label="Provide with entities separated by commas", value="", height=150, max_chars=400)
    # Submit button
    if st.button('Submit'):
        role = "You are an expert in relational database technologies"
        prompt = f"""You need to design a database compatible with MySQL database. 
                The name of the database is {db_name}
                The Entities you need to use are {entities}
                
                These are your tasks:
                First: Generate the complete SQL that can be executed in MySQL system. 
                Second: If you feel any additional entities will add value, feel free to add them based on your knowledge and your understanding of the given entities. 
                Where applicable, design the constraints and foreign key relationships between the entities. 
                Where possible, add a database-friendly comment section to add a few details about the entity.                 
                
                Display the results as: 
                Based on the information provided the generated SQL is:
"""
        # run the LLM model
        with st.spinner("Processing ... please wait."):
            model_response = run_LLM(prompt, role)
            if model_response:
                st.markdown(model_response.content, unsafe_allow_html=True)
                st.write("---")

# Logic for Code Assistant
elif option == 'Code Assistant':
    # File upload box that accepts only text files
    uploaded_file = st.file_uploader(label="Upload the code in .txt file format...", type="txt")
    # give more options
    col3, col4 = st.columns([3, 3], gap="small")
    with col3:
        code_target = st.radio("What you need to do with the code file?", options=['Display On Page', 'Generate Documentation', 'Generate Flow Diagram', 'Convert Code', 'Generate Boilerplate Python Code'])
        if code_target == "Convert Code":
            target_options = ['Python', 'Java', 'SQL', 'Node.js']
            with col4:
                target_code_language = st.selectbox("Select the Target Platform", target_options)
    # Submit button
    if st.button('Submit'):
        if uploaded_file is not None:
            file_content = uploaded_file.read().decode("utf-8")
            if code_target == "Display On Page":
                st.code(file_content)
            else:
                role = "You are an expert in generating technical design documents" if code_target == "Generate Documentation" else "You are an expert in generating mermaid script" if code_target == "Generate Flow Diagram" else "You are an expert programmer" if code_target == "Convert Code" else "You are an expert in generating boilerplate code"
                prompt = f"""You have been provided with the code. 
                        These are your tasks:
                        First, identify the code type - whether it's Python, script, SQL, or something else.
                        {"Generate a technical design document ensuring all important processes are documented in detail." if code_target == "Generate Documentation" else "Generate a mermaid script to build the process flow by analyzing the code." if code_target == "Generate Flow Diagram" else f"Convert the code to the target language {target_code_language}. If the source and target programming language is the same, just display the code without any modifications." if code_target == "Convert Code" else "Generate a boilerplate Python code template from the provided mermaid script."}
                        Display the results as: 
                        Identified Code is:
                        {"Technical Documentation:" if code_target == "Generate Documentation" else "Mermaid Script to generate flow diagram is:" if code_target == "Generate Flow Diagram" else f"Target Conversion is: {target_code_language}\nConverted Code is:" if code_target == "Convert Code" else "Boilerplate Python Code:"}
                        The code given is: {file_content}
"""
                # run the LLM model
                with st.spinner("Processing ... please wait."):
                    model_response = run_LLM(prompt, role)
                    if model_response:
                        st.markdown(model_response.content, unsafe_allow_html=True)
                        if code_target == "Generate Flow Diagram":
                            st.markdown("Use the mermaid script in open-source tools like draw.io to generate the diagram.")
        else:
            st.warning("Please upload the code in .txt file format ... ")
            st.stop()
