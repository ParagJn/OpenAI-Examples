## Generate images using DALL.E
## Requires openai api key
## built using streamlit UI framework
## parag.jn@gmail.com
## August 2024

import streamlit as st
import requests
import os
import random
import string
from openai_client import OpenAIClient  # OpenAI connector class

def initialize_client():
    openai_client_obj = OpenAIClient()
    return openai_client_obj.get_client()

def generate_unique_filename():
    # Create a random alphanumeric string of 5 characters
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
    unique_filename = f"image_generator_{random_string}"
    return unique_filename

def setup_images_folder(images_folder="images"):
    images_dir = os.path.join(os.curdir, images_folder)
    if not os.path.isdir(images_dir):
        os.mkdir(images_dir)
    return images_dir

# main function that calls DALL-E model to generate the image
def generate_image(client, prompt, image_dimension, quality, style):
    return client.images.generate(
        model="dall-e-3",
        size=image_dimension,
        prompt=prompt,
        n=1,
        response_format="url",
        quality=quality,
        style=style
    )

#save image for it to be displayed to page
def save_image(image_url, image_path):
    """Save the generated image from URL to the specified path."""
    generated_image = requests.get(image_url).content
    
    with open(image_path, "wb") as image_file:
        image_file.write(generated_image)

#display the image on canvas
def display_image(image_path, width):
    """Display the generated image using Streamlit."""
    st.image(image_path, width=width)
    st.success(f"Image generated successfully. Hope you like it. Right-click and use Save As to save the image...")

def main():
    # Initialize OpenAI Client
    client = initialize_client()

    # Setting up images directory
    images_dir = setup_images_folder()

    # Streamlit app layout
    st.set_page_config(page_title="DALL-E Image Generator", layout="wide")

    # Sidebar options
    st.sidebar.title("Image Settings")
    image_dimension = st.sidebar.radio("Select Image Dimension", ['1024x1024', '1024x1792','1792x1024'])
    quality = st.sidebar.radio("Select Quality", ["standard","hd"])
    style = st.sidebar.radio("Select Style", ["vivid", "natural"])

    # Text input for prompt
    st.title("DALL-E Image Generator")
    image_prompt = st.text_area("Enter the Image Prompt:", height=150)

    # Submit button
    if st.button("Generate Image"):
        if not image_prompt.strip():
            st.error("Prompt cannot be empty!")
        else:
            try:
                with st.spinner("Generating image..."):
                    # Generate the image
                    model_response = generate_image(client, image_prompt, image_dimension, quality, style)

                    generated_image_name = generate_unique_filename()
                    generated_image_filepath = os.path.join(images_dir, generated_image_name)
                    generated_image_url = model_response.data[0].url
                    save_image(generated_image_url, generated_image_filepath)       # save the image
                    image_width = int(image_dimension.split('x')[0])    # Display the generated image, use the orignal dimensions
                    display_image(generated_image_filepath, image_width)

            except Exception as e:
                st.error(f"An error occurred: {e}")
    st.write("---")

    with st.sidebar:
        st.write("---")
        #setup to display the existing images. 
        image_files = os.listdir(images_dir)
        image_files.insert(0,'None')    # hard coded None as first element in the list. 
        selected_image = st.sidebar.selectbox("Select an Image to Display", image_files,)

    if selected_image != 'None':
        # if an image is selected only then display
        selected_image_path = os.path.join(images_dir, selected_image)
        st.image(selected_image_path, caption=selected_image, use_column_width=True)

if __name__ == "__main__":
    main()
