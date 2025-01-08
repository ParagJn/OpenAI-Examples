###
# Describe the image using google's gemini flash 2.0 experimental model. 
# parag.jn@gmail.com
# Requires a valid API key from google's generativeai. Set it up in the environment variables.
###
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
import io

# API Key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def save_file_locally(uploaded_file):
    """Save the uploaded file locally.
    param: uploaded_file: The uploaded file object.
    return: The path where the file is saved.
    """
    try:
        save_path = os.path.join("uploads", uploaded_file.name)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        return save_path
    except Exception as e:
        st.error(f"Error saving file locally: {e}")
        return None

def describe_image_with_url(image_url):
    """Generates a description for the image using its URL.
    param: image_url: The URL of the image to describe.
    return: The generated description.
    """
    prompt = """Generate a short description of the image. Keep it less than 200 words. 
    Also, generate the hashtags that are appropriate for the image.
"""
    try:
        file = genai.upload_file(image_url, mime_type="image/jpeg")
        print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    except Exception as e:  # hope, no upload errors, if any catch and display the message
        print(f"Error uploading file: {e}")
    
    try:
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

# model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 900,
    "response_mime_type": "text/plain",
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
st.title("Gemini Image Description")

uploaded_file = st.file_uploader("Upload an image (PNG, JPEG, JPG)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image_bytes = uploaded_file.getvalue()
    try:
        image = Image.open(io.BytesIO(image_bytes))
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
                    st.write(description)
        else:
            st.error("Failed to save the file locally.")
    except Exception as e:
        st.error(f"Error processing the uploaded file: {e}")
