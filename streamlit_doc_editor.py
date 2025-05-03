"""
Document editing using OpenAI GPT models.
- Allows document upload (txt, docx), iterative prompt-based editing, and context-aware enhancements.
- Extracts and saves images from docx files.
- Lets user download the final document (with images) as a Word file.
- Model and generation parameters are configurable in the sidebar.
- Parag.Jn@Gmail.com
"""

import streamlit as st
from IBM_GPT_Connector import AzureAIConnection
import os

class PageConfig:
    """
    Handles Streamlit page configuration for layout and sidebar.
    """
    @staticmethod
    def set():
        """
        Set the Streamlit page configuration to wide layout with sidebar expanded.
        """
        st.set_page_config(
            page_title="GPT Document Editor",
            layout="wide",
            initial_sidebar_state="expanded"
        )

def ensure_image_folder():
    """
    Ensures the image folder exists for saving extracted images.

    Returns:
        str: The absolute path to the images folder.
    """
    img_folder = os.path.join(os.getcwd(), "document", "images")
    os.makedirs(img_folder, exist_ok=True)
    return img_folder

def extract_images_from_docx(file, img_folder):
    """
    Extracts images from a docx file and saves them to the specified folder.

    Args:
        file: The uploaded docx file object.
        img_folder (str): Path to the folder where images will be saved.

    Returns:
        list: List of file paths to the saved images.
    """
    from docx import Document
    from docx.image.image import Image
    import shutil

    images = []
    doc = Document(file)
    rels = doc.part.rels
    for rel in rels:
        rel_obj = rels[rel]
        if "image" in rel_obj.target_ref:
            img_part = rel_obj.target_part
            img_data = img_part.blob
            img_name = os.path.basename(img_part.partname)
            img_path = os.path.join(img_folder, img_name)
            with open(img_path, "wb") as f:
                f.write(img_data)
            images.append(img_path)
    return images

def read_file(file):
    """
    Reads the uploaded file and extracts text and images (if docx).

    Args:
        file: The uploaded file object.

    Returns:
        tuple: (document_text, images_list)
    """
    if file.type == "text/plain":
        return file.read().decode("utf-8"), []
    elif file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        import docx
        img_folder = ensure_image_folder()
        images = extract_images_from_docx(file, img_folder)
        doc = docx.Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text, images
    else:
        return None, []

def update_document(azure_client, deployment_name, messages, temperature, max_tokens, top_p, presence_penalty, frequency_penalty):
    """
    Calls the Azure OpenAI API to update the document based on the conversation history and user prompt.

    Args:
        azure_client: AzureOpenAI client instance.
        deployment_name (str): Azure deployment name.
        messages (list): List of message dicts for the chat API.
        temperature (float): Sampling temperature.
        max_tokens (int): Maximum tokens in response.
        top_p (float): Nucleus sampling parameter.
        presence_penalty (float): Presence penalty.
        frequency_penalty (float): Frequency penalty.

    Returns:
        str: The updated document text.
    """
    response = azure_client.chat.completions.create(
        model=deployment_name,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        presence_penalty=presence_penalty,
        frequency_penalty=frequency_penalty,
    )
    return response.choices[0].message.content.strip()

def generate_docx(text, images):
    """
    Generates a Word document from the provided text and images.

    Args:
        text (str): The document text.
        images (list): List of image file paths.

    Returns:
        BytesIO: In-memory Word document for download.
    """
    from docx import Document
    from docx.shared import Inches
    doc = Document()
    for para in text.split("\n"):
        doc.add_paragraph(para)
    # Add images at the end (or you can customize placement)
    for img_path in images:
        doc.add_picture(img_path, width=Inches(4))
    from io import BytesIO
    output = BytesIO()
    doc.save(output)
    output.seek(0)
    return output

def main():
    """
    Main function to run the Streamlit app.
    Handles UI, user interaction, document editing, and download.
    """
    PageConfig.set()
    st.sidebar.title("Settings")

    # Sidebar model and parameter settings
    model_options = {
        "GPT-4o": "gpt-4o",
        "GPT-4o Mini": "gpt-4o-mini",
        "GPT-4.1": "gpt-4-1106-preview"
    }
    model_label = st.sidebar.selectbox("Model", list(model_options.keys()), index=0)
    model = model_options[model_label]
    temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.2, 0.05)
    max_tokens = st.sidebar.slider("Max Tokens", 256, 4096, 2048, 64)
    top_p = st.sidebar.slider("Top-p", 0.0, 1.0, 1.0, 0.05)
    presence_penalty = st.sidebar.slider("Presence Penalty", -2.0, 2.0, 0.0, 0.1)
    frequency_penalty = st.sidebar.slider("Frequency Penalty", -2.0, 2.0, 0.0, 0.1)

    st.title("GPT Document Editor")
    st.write("Upload a document, describe the changes you want, and let GPT update it for you.")

    # Initialize Azure AI connection
    try:
        azure_ai_connection = AzureAIConnection()
        azure_client = azure_ai_connection.get_client()
        deployment_name = azure_ai_connection.get_deployment_name()
    except Exception as e:
        st.error(f"Failed to initialize Azure OpenAI connection: {e}")
        return

    # Session state for context-aware, iterative editing
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_doc" not in st.session_state:
        st.session_state.current_doc = None
    if "history" not in st.session_state:
        st.session_state.history = []
    if "images" not in st.session_state:
        st.session_state.images = []

    uploaded_file = st.file_uploader("Upload your document", type=["txt", "docx"])
    if uploaded_file and st.session_state.current_doc is None:
        document_text, images = read_file(uploaded_file)
        if not document_text:
            st.error("Unsupported file type or failed to read the document.")
            return
        # Initialize conversation
        system_prompt = (
            "You are a helpful assistant. The user will provide a document and a prompt describing changes to make. "
            "Return the updated document as plain text, reflecting the requested changes. "
            "If the user provides further prompts, continue editing the latest version of the document."
        )
        st.session_state.messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Document:\n{document_text}"}
        ]
        st.session_state.current_doc = document_text
        st.session_state.history = []
        st.session_state.images = images

    if st.session_state.current_doc:
        st.subheader("Describe the changes you want to make:")
        user_prompt = st.text_area("Enter your instructions here...", height=100, key="prompt_area")
        col1, col2, col3 = st.columns([1,1,1])
        submit = col1.button("Submit Changes")
        reset = col2.button("Start Over")
        finalize = col3.button("Finalize & Download")
        if reset:
            st.session_state.current_doc = None
            st.session_state.messages = []
            st.session_state.history = []
            st.session_state.images = []
            st.rerun()
        if submit and user_prompt.strip():
            with st.spinner("Updating document...", show_time=True):
                st.session_state.messages.append({"role": "user", "content": f"Change request: {user_prompt}"})
                try:
                    updated_doc = update_document(
                        azure_client,
                        deployment_name,
                        st.session_state.messages,
                        temperature,
                        max_tokens,
                        top_p,
                        presence_penalty,
                        frequency_penalty
                    )
                    st.session_state.messages.append({"role": "assistant", "content": updated_doc})
                    st.session_state.current_doc = updated_doc
                    st.session_state.history.append(user_prompt)
                    st.success("Document updated successfully!")
                except Exception as e:
                    st.error(f"Error updating document: {e}")

        if st.session_state.current_doc:
            st.subheader("Updated Document:")
            st.text_area("Result", value=st.session_state.current_doc, height=400, key="result_area")

            if st.session_state.images:
                st.markdown("**Extracted Images:**")
                for img_path in st.session_state.images:
                    st.image(img_path, width=200)

            if st.session_state.history:
                st.markdown("**Enhancement History:**")
                for idx, prompt in enumerate(st.session_state.history, 1):
                    st.markdown(f"{idx}. {prompt}")

            if finalize:
                with st.spinner("Generating Word document..."):
                    docx_file = generate_docx(st.session_state.current_doc, st.session_state.images)
                    st.success("Word document generated!")
                    st.download_button(
                        label="Download Updated Document",
                        on_click="ignore",
                        data=docx_file,
                        file_name="updated_document.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

if __name__ == "__main__":
    main()