import streamlit as st
import os
import json
import google.generativeai as genai
from PIL import Image
import io
from datetime import datetime

# Set page configuration
st.set_page_config(
    layout="wide",
    page_title="Generate Image Description",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "### An app that describes the image using Google's Gemini model. \nConnect with me email:parag.jn@gmail.com if needed for any help.",
    }
)

# Sidebar configuration
with st.sidebar:
    st.title("Model Configuration")
    max_output_tokens = st.number_input("Max Output Tokens", min_value=100, max_value=5000, value=900, step=100)
    temperature = st.slider("Temperature", min_value=0.1, max_value=1.0, value=1.0, step=0.1)
    response_type = st.selectbox("Response Type", ["text/plain", "application/json"], index=0)

    # TODO: Fix the log display issue. 
    # # Radio button to display previous generations
    # display_previous = st.radio(
    #     "Display Previous Generations", 
    #     options=["No", "Yes"], 
    #     index=0
    # )


# API Key configuration
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def save_file_locally(uploaded_file):
    """Save the uploaded file locally."""
    try:
        save_path = os.path.join("uploads", uploaded_file.name)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        return save_path
    except Exception as e:
        st.error(f"Error saving file locally: {e}")
        return None

def log_output(image_name, description):
    """Log the output to image_description.json."""
    log_file = "image_description.json"
    log_entry = {
        "image_name": image_name,
        "date": datetime.now().isoformat(),
        "description": description,
    }
    try:
        if not os.path.exists(log_file):
            with open(log_file, "w") as file:
                json.dump([log_entry], file, indent=4)
        else:
            with open(log_file, "r+") as file:
                data = json.load(file)
                data.append(log_entry)
                file.seek(0)
                json.dump(data, file, indent=4)
    except Exception as e:
        st.error(f"Error logging output: {e}")

def describe_image_with_url(image_url):
    """Generates a description for the image using its URL."""
    prompt = """Generate a short description of the image. Keep it less than 200 words. 
    Also, generate the hashtags that are appropriate for the image."""
    try:
        file = genai.upload_file(image_url, mime_type="image/jpeg")
        chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        file,
                        f"{prompt}",
                    ],
                },
            ]
        )
        response = chat_session.send_message("Describe the image in detail")
        return response.text
    except Exception as e:
        st.error(f"Error generating image description: {e}")
        return None

# Model configuration
generation_config = {
    "temperature": temperature,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": max_output_tokens,
    "response_mime_type": response_type,
}

# Initialize the model
try:
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        generation_config=generation_config,
    )
except Exception as e:
    st.error(f"Error initializing model: {e}")

# Streamlit app layout
st.title("Generate Image Description")
st.markdown("This app uses Google's Gemini Model - gemini-2.0-flash-exp")
st.markdown("**Requires a valid API key from google's generativeai. Set it up in the environment variables**")

uploaded_file = st.file_uploader("Upload an image (PNG, JPEG, JPG)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image_bytes = uploaded_file.getvalue()
    try:
        image = Image.open(io.BytesIO(image_bytes))
        with st.sidebar:
            st.image(image, caption="Uploaded Image.", use_container_width=True)

        # Save the file locally
        local_path = save_file_locally(uploaded_file)
        if local_path:
            st.write(f"File saved locally at: {local_path}")
            # Replace with a hosted file URL if required
            image_url = f"{os.path.abspath(local_path)}"
            with st.spinner('Generating description...'):
                description = describe_image_with_url(image_url)
                if description:
                    st.write("### Image Description:")
                    if response_type == "text/plain":
                        st.write(description)
                    else:
                        st.json(description)

                    # Log the output
                    log_output(uploaded_file.name, description)
        else:
            st.error("Failed to save the file locally.")
    except Exception as e:
        st.error(f"Error processing the uploaded file: {e}")

# TODO: Fix this to display the log properly and not rerun the llm call. 

# # Display previous generations if "Yes" is selected
# if display_previous == "Yes":
#     log_file = "image_description.json"
#     st.write("Review the previously generated image descriptions:")
#     if os.path.exists(log_file):
#         with open(log_file, "r") as file:
#             data = json.load(file)
#             st.json(data)
#     else:
#         st.write("No previous generations found.")
