"""
Image Converter Module

This module provides functionality to convert images to markdown format with metadata and descriptions.
It utilizes a custom markdown converter and integrates with a language model to generate detailed captions for images.

Classes:
    _CustomMarkdownify: A custom version of markdownify's MarkdownConverter for image handling.
    DocumentConverterResult: Represents the result of converting a document to text.
    ImageConverter: Converts images to markdown with metadata and descriptions.

Functions:
    test_image_conversion: Tests the image conversion functionality (commented out).Use this function to test the image conversion functionality.

Parag Jain
"""

import base64
import mimetypes
from typing import Any, Union
import markdownify
from tiktoken import Encoding, get_encoding
import os
from App_Logger import get_logger

# Start the logging feature
logger = get_logger()

class _CustomMarkdownify(markdownify.MarkdownConverter):
    """A custom version of markdownify's MarkdownConverter for image handling."""

    def __init__(self, **options: Any):
        options["heading_style"] = options.get("heading_style", markdownify.ATX)
        super().__init__(**options)

    def convert_img(self, el: Any, text: str, convert_as_inline: bool) -> str:
        """
        Converts image elements to markdown format.

        Args:
            el (Any): The element to convert.
            text (str): The text content of the element.
            convert_as_inline (bool): Whether to convert as inline.

        Returns:
            str: The converted markdown string.
        """
        alt = el.attrs.get("alt", None) or ""
        src = el.attrs.get("src", None) or ""
        title = el.attrs.get("title", None) or ""
        title_part = ' "%s"' % title.replace('"', r'\"') if title else ""
        
        if convert_as_inline and el.parent.name not in self.options["keep_inline_images_in"]:
            return alt

        # Remove dataURIs
        if src.startswith("data:"):
            src = src.split(",")[0] + "..."

        return "![%s](%s%s)" % (alt, src, title_part)

class DocumentConverterResult:
    """The result of converting a document to text."""

    def __init__(self, title: Union[str, None] = None, text_content: str = ""):
        """
        Initializes a DocumentConverterResult instance.

        Args:
            title (Union[str, None], optional): The title of the document. Defaults to None.
            text_content (str, optional): The text content of the document. Defaults to "".
        """
        self.title: Union[str, None] = title
        self.text_content: str = text_content

class ImageConverter:
    """Converts images to markdown with metadata and descriptions."""
    
    def __init__(self):
        """Initializes the ImageConverter instance and tokenizer."""
        self.tokenizer = get_encoding("o200k_base")  # encoding for GPT-4o-mini

    def convert(self, local_path: str, **kwargs: Any) -> Union[None, DocumentConverterResult]:
        """
        Converts an image to markdown format with metadata and descriptions.

        Args:
            local_path (str): The local path to the image file.
            **kwargs (Any): Additional keyword arguments for LLM client and model configuration.

        Returns:
            Union[None, DocumentConverterResult]: The result of the conversion, or None if an error occurs.
        """
        try:
            # Define valid image file extensions
            valid_extensions = {".jpg", ".jpeg", ".png"}

            # Dynamically extract the file extension from the provided local path
            _, extension = os.path.splitext(local_path)
            extension = extension.lower()

            # Check if the extension is valid
            if extension not in valid_extensions:
                print(f"Invalid file extension: {extension}")
                return None

            # checking for LLM client configuration
            llm_client = kwargs.get("llm_client")
            llm_model = kwargs.get("llm_model")
            if llm_client is None or llm_model is None:
                print("LLM client or model not provided.")
                return None

            # Calculate input tokens
            input_text = kwargs.get("llm_prompt", "Write a detailed caption for this image.")
            input_tokens = len(self.tokenizer.encode(input_text))
            logger.info(f"Input Tokens to generate image: {input_tokens}")
            print(f"Input Tokens: {input_tokens}")

            md_content = (
                "\n# Description:\n"
                + self._get_llm_description(
                    local_path,
                    extension,
                    llm_client,
                    llm_model,
                    prompt=input_text,
                ).strip()
                + "\n"
            )

            return DocumentConverterResult(
                title=None,
                text_content=md_content,
            )
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def _get_llm_description(self, local_path, extension, client, model, prompt=None):
        """
        Generates a detailed description for the image using a language model.

        Args:
            local_path (str): The local path to the image file.
            extension (str): The file extension of the image.
            client (Any): The LLM client instance.
            model (str): The LLM model to use.
            prompt (str, optional): The prompt to use for generating the description. Defaults to None.

        Returns:
            str: The generated description.
        """
        if prompt is None or prompt.strip() == "":
            prompt = "Write a detailed caption for this image."

        data_uri = ""
        with open(local_path, "rb") as image_file:
            content_type, encoding = mimetypes.guess_type("_dummy" + extension)
            if content_type is None:
                content_type = "image/jpeg"
            image_base64 = base64.b64encode(image_file.read()).decode("utf-8")
            data_uri = f"data:{content_type};base64,{image_base64}"

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": data_uri,
                        },
                    },
                ],
            }
        ]

        response = client.chat.completions.create(model=model, messages=messages)

        # Calculate output tokens
        response_content = response.choices[0].message.content
        output_tokens = len(self.tokenizer.encode(response_content))
        logger.info(f"Output Tokens from image: {output_tokens}")
        print(f"Output Tokens: {output_tokens}")

        return response_content

# # test the code here
# from openai import OpenAI
# import os
# from dotenv import load_dotenv  # You'll need to pip install python-dotenv

# def test_image_conversion():
#     """
#     Tests the image conversion functionality.
#     Loads environment variables, initializes the OpenAI client, and converts a sample image.
#     """
#     # Load environment variables from .env file
#     load_dotenv()
    
#     # Initialize OpenAI client using API key from environment variable
#     client = OpenAI(
#         api_key=os.getenv('OPENAI_API_KEY')
#     )
    
#     # Create an instance of ImageConverter
#     converter = ImageConverter()
    
#     # Test with a sample image
#     test_image_path = "/root/coding-works/openai-experiments/exports/process-flow.jpg" 
    
#     # Convert image to markdown with LLM configuration
#     result = converter.convert(
#         test_image_path, 
#         llm_client=client,
#         llm_model="gpt-4o-mini",
#         llm_prompt="Describe the given image in detail"
#     )
    
#     if result:
#         print("Conversion successful!")
#         print("\nTitle:", result.title)
#         print("\nContent:", result.text_content)
#     else:
#         print("Conversion failed!")

# # Create a .env file and use it
# if __name__ == "__main__":
#     test_image_conversion()