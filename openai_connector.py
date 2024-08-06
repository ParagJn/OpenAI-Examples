"""
Program Overview:
This module, `OpenAIConnector`, provides an interface for connecting to the OpenAI API, with functionalities 
for validating API keys and generating text summaries using various OpenAI models. It supports a selection of 
models, including 'gpt-4', 'gpt-4o', 'gpt-4-turbo', 'gpt-4o-mini', and 'gpt-3.5-turbo'. The API key is securely 
loaded from environment variables, and the module ensures that the key is valid before allowing further API interactions.

Key Features:
- Load API key from environment variables using dotenv.
- Validate the API key with OpenAI.
- Generate text summaries using specified OpenAI models.
- Raise custom exceptions for invalid API keys.

Dependencies:
- os
- openai
- python-dotenv (dotenv)
- openai_exceptions (custom module for handling exceptions)

Author: parag.jn@gmail.com
Date: August 2024
"""

import os
import openai
from dotenv import load_dotenv
from openai_exceptions import InvalidAPIKeyError

class OpenAIConnector:
    model_choices = ['none', 'gpt-4', 'gpt-4o', 'gpt-4-turbo', 'gpt-4o-mini', 'gpt-3.5-turbo']

    def __init__(self, api_key_env_var='api_key'):
        load_dotenv()
        api_key = os.getenv(api_key_env_var)
        if api_key is None:
            raise ValueError("API key not found in environment variables.")
        
        openai.api_key = api_key

        # Validate the API key
        if not self._is_valid_api_key():
            raise InvalidAPIKeyError()

    def _is_valid_api_key(self):
        try:
            openai.Model.list()  # Make a simple API call to check for a valid API key
            return True
        except openai.error.AuthenticationError:
            return False

    def summarize_text(self, text, model="none", prompt="You are a helpful assistant."):
        if model == "none":
            raise ValueError("Select a model to continue ...")
        
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ],
            max_tokens=3500
        )
        return response.choices[0].message['content'].strip()