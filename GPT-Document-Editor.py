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

from image_utils import ImageHandler
from document_utils import read_file

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

def update_document(azure_client, deployment_name, messages, temperature, max_tokens):
    """
    Calls the Azure OpenAI API to update the document based on the conversation history and user prompt.

    Args:
        azure_client: AzureOpenAI client instance.
        deployment_name (str): Azure deployment name.
        messages (list): List of message dicts for the chat API.
        temperature (float): Sampling temperature.
        max_tokens (int): Maximum tokens in response.

    Returns:
        str: The updated document text.
    """
    response = azure_client.chat.completions.create(
        model=deployment_name,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()

def generate_docx(text, images, original_docx_file=None):
    """
    Generates a Word document from the provided text and images.
    If original_docx_file is provided, tries to preserve image positions,
    but always uses the latest edited text for paragraphs.

    Args:
        text (str): The document text.
        images (list): List of image file paths.
        original_docx_file: The original uploaded docx file object (optional).

    Returns:
        BytesIO: In-memory Word document for download.
    """
    from docx import Document
    from docx.shared import Inches
    from io import BytesIO

    new_doc = Document()
    text_lines = text.split("\n")

    if original_docx_file and images:
        try:
            original_doc = Document(original_docx_file)
            img_idx = 0
            para_img_map = []
            for para in original_doc.paragraphs:
                has_image = any("graphic" in run._element.xml for run in para.runs)
                para_img_map.append(has_image)
            for i, para_text in enumerate(text_lines):
                new_doc.add_paragraph(para_text)
                if i < len(para_img_map) and para_img_map[i] and img_idx < len(images):
                    img_path = images[img_idx]
                    if ImageHandler.is_supported_for_docx(img_path):
                        new_doc.add_picture(img_path, width=Inches(4))
                    img_idx += 1
            while img_idx < len(images):
                img_path = images[img_idx]
                if ImageHandler.is_supported_for_docx(img_path):
                    new_doc.add_picture(img_path, width=Inches(4))
                img_idx += 1
        except Exception:
            for para in text_lines:
                new_doc.add_paragraph(para)
            for img_path in images:
                if ImageHandler.is_supported_for_docx(img_path):
                    new_doc.add_picture(img_path, width=Inches(4))
    else:
        for para in text_lines:
            new_doc.add_paragraph(para)
        for img_path in images:
            if ImageHandler.is_supported_for_docx(img_path):
                new_doc.add_picture(img_path, width=Inches(4))

    output = BytesIO()
    new_doc.save(output)
    output.seek(0)
    return output

def reset_app_state():
    """
    Resets the Streamlit session state for a fresh start.
    """
    st.session_state.current_doc = None
    st.session_state.messages = []
    st.session_state.history = []
    st.session_state.original_docx_file = None

    # Delete all images generated and their previews
    for img in st.session_state.images:
        ImageHandler.delete_image_and_preview(img)
    st.session_state.images = []
    st.session_state.checked_images = []


def is_prompt_relevant(prompt, document_text):
    """
    Checks if the user prompt is relevant to the uploaded document.
    Returns True if relevant, False otherwise.
    """
    # Simple heuristic: at least one word from the prompt should appear in the document (case-insensitive, ignoring stopwords)
    import re
    stopwords = set([
        "the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "with", "at", "by", "from", "as", "is", "are", "was", "were", "be", "this", "that", "it", "you", "i"
    ])
    prompt_words = set(re.findall(r'\b\w+\b', prompt.lower())) - stopwords
    doc_words = set(re.findall(r'\b\w+\b', document_text.lower()))
    return bool(prompt_words & doc_words)

def main():
    """
    Main function to run the Streamlit app.
    Handles UI, user interaction, document editing, and download.
    """
    PageConfig.set()
    st.sidebar.title("Settings :gear:")
    st.logo("./business friendly llm ai based document editor.png",size="large")

    # Sidebar model and parameter settings
    model_options = {
        "GPT-4o": "gpt-4o",
        "GPT-4o Mini": "gpt-4o-mini"        
    }
    model_label = st.sidebar.selectbox("Model", list(model_options.keys()), index=1)
    model = model_options[model_label]
    temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.2, 0.05)
    max_tokens = st.sidebar.slider("Max Tokens", 256, 4096, 2048, 64)
    st.sidebar.markdown("---")

    doc_processor, dsx_processor = st.tabs(["Document Processor", "DSX Processor"])

    with doc_processor:

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
        if "checked_images" not in st.session_state:
            st.session_state.checked_images = []

        uploaded_file = st.file_uploader("Upload your document", type=["txt", "docx"])
        # Reset app if file is deleted after upload
        if uploaded_file is None and st.session_state.get("current_doc") is not None:
            reset_app_state()
            st.rerun()

        if uploaded_file and st.session_state.current_doc is None:
            document_text, images = read_file(uploaded_file)
            if not document_text:
                st.error("Unsupported file type or failed to read the document.")
                return
            # Initialize conversation
            st.badge("Document is loaded & parsed...", icon=":material/check:", color="green")
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
            st.session_state.checked_images = [False] * len(images)
            st.session_state.original_docx_file = uploaded_file if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" else None

        if st.session_state.current_doc:
            st.subheader("Describe the changes you want to make to the document :point_down:")
            user_prompt = st.text_area("Enter your instructions here...", height=100, key="prompt_area")
            col1, col2, col3 = st.columns([1,1,1])
            submit = col1.button("Submit Changes")
            reset = col2.button("Start Over")
            finalize = col3.button("Finalize & Download")
            if reset:
                reset_app_state()
                st.rerun()
            if submit and user_prompt.strip():
                # Check prompt relevance before sending to model
                if not is_prompt_relevant(user_prompt, st.session_state.current_doc):
                    st.warning("Please provide instructions that are relevant to the uploaded document.")
                else:
                    with st.spinner("Updating document...", show_time=True):
                        st.session_state.messages.append({"role": "user", "content": f"Change request: {user_prompt}"})
                        try:
                            updated_doc = update_document(
                                azure_client,
                                deployment_name,
                                st.session_state.messages,
                                temperature,
                                max_tokens
                            )
                            st.session_state.messages.append({"role": "assistant", "content": updated_doc})
                            st.session_state.current_doc = updated_doc
                            st.session_state.history.append(user_prompt)
                            st.badge("Document updated -- Review the content below :point_down:", icon=":material/check:", color="green")
                            
                        except Exception as e:
                            st.error(f"Error updating document: {e}")

            if st.session_state.current_doc:
                st.subheader("Content extracted from the document:")
                st.text_area("Result", value=st.session_state.current_doc, height=400, key="result_area")

                if st.session_state.images:
                    st.markdown("**Extracted Images:**")
                    # Always sync checked_images length with images length
                    if len(st.session_state.checked_images) != len(st.session_state.images):
                        st.session_state.checked_images = [False] * len(st.session_state.images)
                    checked_images = []
                    for idx, img_path in enumerate(st.session_state.images):
                        col_img, col_chk = st.columns([4,1])
                        ext = os.path.splitext(img_path)[1].lower()
                        # Always display PNG version if available (for .emf/.wmf)
                        display_path = img_path
                        if ext in [".emf", ".wmf"]:
                            png_path = ImageHandler.convert_emf_to_png(img_path)
                            if png_path and os.path.exists(png_path):
                                display_path = png_path
                                col_img.image(display_path, width=200, caption=f"Preview of {os.path.basename(img_path)}")
                            else:
                                col_img.warning(f"Image format not supported for preview: {os.path.basename(img_path)}")
                        elif ImageHandler.is_supported_for_preview(img_path):
                            col_img.image(img_path, width=200)
                        else:
                            col_img.warning(f"Image format not supported for preview: {os.path.basename(img_path)}")
                        checked = col_chk.checkbox("Select", value=st.session_state.checked_images[idx], key=f"img_chk_{idx}")
                        checked_images.append(checked)
                    st.session_state.checked_images = checked_images

                    if st.sidebar.button("Delete Selected Images"):
                        new_images = []
                        new_checked = []
                        for img, checked in zip(st.session_state.images, st.session_state.checked_images):
                            if not checked:
                                new_images.append(img)
                                new_checked.append(False)
                            else:
                                ImageHandler.delete_image_and_preview(img)
                        st.session_state.images = new_images
                        st.session_state.checked_images = new_checked
                        st.sidebar.success("Selected images deleted.")
                        st.rerun()

                if st.session_state.history:
                    st.markdown("**Enhancement History:**")
                    for idx, prompt in enumerate(st.session_state.history, 1):
                        st.markdown(f"{idx}. {prompt}")

                if finalize:
                    with st.spinner("Generating Word document..."):
                        docx_file = generate_docx(
                            st.session_state.current_doc,
                            st.session_state.images,
                            original_docx_file=st.session_state.get("original_docx_file")
                        )
                        st.success("Word document generated!")
                        st.download_button(
                            label="Download Updated Document",
                            on_click="ignore",
                            data=docx_file,
                            file_name="updated_document.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                        # Delete all images and their previews after generating the document
                        for img in st.session_state.images:
                            ImageHandler.delete_image_and_preview(img)
                        st.session_state.images = []
                        st.session_state.checked_images = []
    with dsx_processor:
        st.title("DSX Processor")
        # Placeholder for DSX processor functionality
        st.info("DSX Processor functionality is not yet implemented.")

if __name__ == "__main__":
    main()