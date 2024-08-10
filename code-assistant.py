# Code Assistant
# This application will help the user with 2 things. 
# 1. Generate a logical database design (coming soon)
# 2. Be a coding assistant to do the following : Generate flow diagram in mermaid script, generate documentaiton or perform conversion to a different programming lanugage. 
# Idea is to use these to save some time doing these tasks and thus, productivity gain. 
# parag.jn@gmail.com
# August 2024

import streamlit as st

# Streamlit application setup
st.set_page_config(
    page_title="Open Ai - Code Helper",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# A Code Helper Tool!"
    },
)

# system variables
MODEL = "gpt-4o-2024-08-06"

# open ai connector
from openai_client import OpenAIClient
# Initialize OpenAI Client
openai_client_obj = OpenAIClient()
client = openai_client_obj.get_client()

def run_LLM(prompt,role="You are a helpful assistant"):
    response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {
            "role": "system", 
            "content": role
        },
        {
            "role": "user", 
            "content": prompt
        }
    ],
    max_tokens=2500,
    n=1,
)
    return response.choices[0].message


# Set the title of the application
st.title("A Coding Assitant")
st.write("---")

# Create a sidebar with a title
st.sidebar.title("Select Option")
st.sidebar.write("---")
# Add radio buttons to the sidebar
option = st.sidebar.radio(label="Select Option",options= ['None', 'DB Generator', 'Code Assistant'],label_visibility="hidden")

# Logic for DB Generator
if option == 'DB Generator':
    col1,col2 = st.columns([3,10],gap="small",vertical_alignment="top")
    with col1:
        db_name = st.text_input(label="Provide with database name",value="",max_chars=50)
    with col2:
        entities = st.text_area(label="Provide with entities seperated by commas",value="", height=150,max_chars=400)
    # Submit button
    if st.button('Submit'):
        st.warning("This feature will be added soon.. ")

# Logic for Code Converter
elif option == 'Code Assistant':
    # File upload box that accepts only text files
    uploaded_file = st.file_uploader(label="Upload the code in .txt file format...", type="txt")
    # give more options
    col3, col4, col5  = st.columns([3,3,10],gap="small",vertical_alignment="bottom")
    with col3:
        code_target = st.radio("What you need to do with code file?",options=['Display On Page','Generate Documentation','Generate Flow Diagram','Convert Code'])
        if code_target == "Convert Code":
            target_options = ['Python','Java','SQL','Node.js']
            with col4:
                target_code_language = st.selectbox("Select the Target Platform",target_options)
    # Submit button
    if st.button('Submit'):
        if uploaded_file is not None:
            file_content = uploaded_file.read().decode("utf-8")
            if code_target == "Display On Page":
                st.code(file_content)
            elif code_target == "Generate Documentation":
                role = "You are an expert in generating technical design documents"
                prompt = f"""You have been provided with the code. 
                        These are your tasks
                        First: using the syntax, identify the code type - weather its python, script, SQL or something else
                        Second: Generate a technical design document ensuring all important processes are documented in detail. 
                        If the syntax identified is SQL then give a small description of each entity
                        If the syntax identified is programming language like python, java, node.js, etc then give a small description of the program and a small description of each identified function. 
                        
                        Display the results as : 
                        Identified Code is :
                        Technical Documentation : 
                        
                        Ensure that document is properly indented and bulletted for better readibility and usability
                        
                        The code given is : {file_content}"""
                model_response = run_LLM(prompt,role)
                if model_response:
                    st.markdown(model_response.content,unsafe_allow_html=True)
            # lets generate a mermaid script first
            elif code_target == "Generate Flow Diagram":
                role = "You are an expert in generating mermaid script"
                prompt = f"""You have been provided with the code. 
                        These are your tasks
                        First using the syntax, identify the code type - weather its python, script, SQL or something else
                        Second, generate a mermid script to build the process flow by analyzing the code
                        Display the results as : 
                        Identified Code is :
                        Mermaid Script to generate flow diagram is : 
                        Ensure that there are no syntax errors in the generated script
                        
                        The code given is : {file_content}"""
                model_response = run_LLM(prompt,role)
                if model_response:
                    st.markdown(model_response.content,unsafe_allow_html=True)
                    st.markdown("Use the mermaid script can be copied to open-source tools like draw.io to generate the diagram.")
            elif code_target == "Convert Code":
                role = "You are an expert programmer"
                prompt = f"""You have been provided with the code. 
                        These are your tasks
                        First using the syntax, identify the code type - weather its python, script, SQL or something else
                        Convert the code in the target language {target_code_language}. If the source and target programming language is same, just display the code without any modifications
                        If the conversion is not possible, display message that between identified source code language and target language, conversion is not possible. 
                        Display the results as : 
                        Identified Code is :
                        Target Conversion is : {target_code_language}
                        Converted Code is : 
                        Where possible, add comments or helpful hints for easier understanding. 
                        Ensure that there are no syntax errors
                        The code given is : {file_content}
                    """
                model_response = run_LLM(prompt,role)
                if model_response:
                    st.markdown(model_response.content,unsafe_allow_html=True)
        else:
            st.warning("Please upload the code in .txt file format ... ")
            st.stop()
