# OpenAI connector class file
# use this to connect with openai using api keys
# requires openai version 1.39 or higher

import os
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st


class OpenAIClient:
    def __init__(self):
        self.openai_client = None
        self.api_key = None
        self._setup()

    def _setup(self):
        try:
            # Load the environment variables
            load_dotenv()
            # Get the API key
            self.api_key = os.getenv("api_key")
            if not self.api_key:
                raise ValueError("API key is not set. Please check your environment variables.")
            
            # Set the OpenAI client
            self.openai_client = OpenAI(api_key=self.api_key)
            self.validate_key()
        except ValueError as e:
            st.error(str(e))
            st.stop()

    def validate_key(self):
        try:
            model_list = self.openai_client.models.list()
            return model_list
        except ValueError as e:
            st.error(str(e))
            st.stop()

    def get_client(self):
        return self.openai_client
