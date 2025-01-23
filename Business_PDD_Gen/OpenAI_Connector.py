# A class file to connect with OpenAI API.
# Parag Jain.

import os
from dotenv import load_dotenv
from openai import OpenAI

class OpenAIClient:
    def __init__(self):
        self.openai_client = None
        self.api_key = None
        self._setup()

    def _setup(self):
        # Load the environment variables
        load_dotenv()
        # Get the API key
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key is not set. Please check your environment variables.")
        
        # Set the OpenAI client
        self.openai_client = OpenAI(api_key=self.api_key)
        self.validate_key()
            
    def validate_key(self):
        try:
            model_list = self.openai_client.models.list()
            return model_list
        except Exception as e:
            raise ValueError(f"An error occurred while validating the API key: {e}")

    def get_client(self):
        return self.openai_client

# Test the class file. 
if __name__ == "__main__":
    openai_client_obj = OpenAIClient()
    client = openai_client_obj.get_client()
    prompt = "hello world"
    model = 'gpt-4o-mini'
    max_tokens = 10

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            n=1,
        )
        print(response.choices[0].message.content.strip())
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
