"""
Program Overview:
This Streamlit application is designed to generate professional posts for various social media platforms
from uploaded image files. The application leverages the OpenAI API for content generation based on user 
inputs and selected social media platforms. The final content is displayed on the screen.

Key Features:
- Upload and process image files.
- Generate professional posts using OpenAI models.
- Display posts directly on the screen in real-time.
- Streamlit-based user interface with customizable model and social media platform options.

Dependencies:
- os
- streamlit
- io
- time
- PIL
- pytesseract (for OCR)

Author: parag.jn@gmail.com
Date: August 2024
"""

import os
import streamlit as st
from PIL import Image
import pytesseract
from openai_connector import OpenAIConnector
import io
import time

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Initialize OpenAI Connector
openai_connector = OpenAIConnector()

# Setting page config
st.set_page_config(
    page_title="Open AI - Social Media Post Generator",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'About': "# Generate professional social media posts from image files!"}
)

def generate_post_from_image(file, model, prompt):
    image = Image.open(file)
    text = pytesseract.image_to_string(image)
    return openai_connector.summarize_text(text, model, prompt)

# Streamlit UI
st.title("Social Media Post Generator")
st.write("---")

# Sidebar Inputs
model_choices = OpenAIConnector.model_choices
model_type = st.sidebar.radio("Choose a model type:", model_choices)

# File uploader
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

if 'user_prompt' not in st.session_state:
    st.session_state.user_prompt = ""

uploaded_file = st.file_uploader("Upload an image file", type=["png", "jpg", "jpeg"])
if uploaded_file:
    st.session_state.uploaded_file = uploaded_file

# Multi-line text box for user prompt
user_prompt = st.text_area("Describe your requirement to build the prompt", value=st.session_state.user_prompt, height=150)
st.session_state.user_prompt = user_prompt


submit = st.button("Submit")

def main():
    def stream_data(data):
        for word in data.split(" "):
            yield word + " "
            time.sleep(0.02)
    
    if submit:
        if st.session_state.uploaded_file is not None:
            try:
                with st.spinner("Generating post..."):
                    if st.session_state.user_prompt:
                        generated_post = generate_post_from_image(st.session_state.uploaded_file, model_type, st.session_state.user_prompt)
                        generated_post = generated_post.replace('$', 'USD')
                        st.write_stream(stream_data(generated_post))
                    else:
                        st.warning("Please provide a description for the prompt.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.warning("Please upload an image file.")

if __name__ == "__main__":
    main()