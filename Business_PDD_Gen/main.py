# main.py = Run the business process design generator application
# Parag Jain

import streamlit as st
from Generate_PDD import ProcessDesignGenerator
import time

# Streamlit UI Page configuration
st.set_page_config(layout="wide",
                       page_icon="🧠",
                       page_title="Generate Business PDD",
                       initial_sidebar_state="expanded")

# Sidebar Content
with st.sidebar:
    st.title("Input Options")
    file_type = st.radio("Upload File", ["Document", "Image"])

# Main content to start the program execution
st.title("Business Process Design Generator")

# Initialize the ProcessDocumentationGenerator
pdd = ProcessDesignGenerator()

# File uploader logic
if file_type == "Document":
    uploaded_files = st.file_uploader("Upload documents", type=['docx'], accept_multiple_files=True)
else:
    uploaded_files = st.file_uploader("Upload images", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Process the uploaded file to generate the PDD
        with st.spinner(f'Processing {uploaded_file.name}...'):
            pdd.process_uploaded_file(uploaded_file.name)
            
        if uploaded_file != uploaded_files[-1]:  # Skip delay for last file
            with st.info(f'Waiting 20 seconds before processing next file...'):
                time.sleep(20)