# main.py = Run the business process design generator application
# Parag Jain

import streamlit as st
from Generate_PDD import ProcessDesignGenerator

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
    uploaded_file = st.file_uploader("Upload a document", type=['docx'])
else:
    uploaded_file = st.file_uploader("Upload an image", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Process the uploaded file to generate the PDD
    pdd.process_uploaded_file(uploaded_file.name)