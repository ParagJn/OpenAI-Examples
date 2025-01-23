# A simple classfile that connects to the Llama model hosted on private cloud instance. 
# Parag Jain. 

import requests
from requests.exceptions import HTTPError, RequestException
from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

class LlamaConnector:
    """
    A connector class for interacting with the IBM Llama model.
    This class handles authentication and communication with the Llama API, 
    enabling users to generate text based on a given prompt.

    Attributes:
        api_key (str): The API key for accessing IBM's services, loaded from environment variables.
        model_id (str): The ID of the Llama model to use, loaded from environment variables.
        project_id (str): The project ID associated with the Llama model, loaded from environment variables.
        ibm_token_url (str): The URL for generating the IBM access token, loaded from environment variables.
        llama_url (str): The base URL for the Llama API, loaded from environment variables.
        ibm_token (str): The generated IBM access token, set dynamically during runtime.
    """

    def __init__(self):
        """
        Initializes the LlamaConnector class by loading configuration from environment variables.
        """
        self.api_key = os.getenv("LLAMA_API_KEY")
        self.model_id = os.getenv("LLAMA_MODEL_ID")
        self.project_id = os.getenv("LLAMA_PROJECT_ID")
        self.ibm_token_url = os.getenv("LLAMA_IBM_TOKEN_URL")
        self.llama_url = os.getenv("LLAMA_BASE_URL")
        self.ibm_token = None

    def get_ibm_access_token(self):
        """
        Fetches the IBM access token using the API key.

        The method sends a POST request to the IBM token URL with the API key 
        to generate an access token. The token is used for authenticating requests 
        to the Llama API.

        Returns:
            str: The IBM access token if the request is successful.

        Raises:
            HTTPError: If the HTTP request returns an unsuccessful status code.
            RequestException: If there are issues with the network request.
            KeyError: If the access token is missing in the response.
            Exception: For any other unexpected errors.
        """
        try:
            print("Generating IBM access token...")
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = f'grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={self.api_key}'

            response = requests.post(self.ibm_token_url, headers=headers, data=data)
            response.raise_for_status()  # Raises HTTPError for bad responses
            
            data = response.json()
            if 'access_token' not in data:
                raise KeyError("Access token not found in the response")

            self.ibm_token = data['access_token']
            print("IBM access token generated successfully.")
            return self.ibm_token

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            print(f'Response content: {response.content}')
        except RequestException as req_err:
            print(f'Request error occurred: {req_err}')
        except KeyError as key_err:
            print(f'Key error: {key_err}')
        except Exception as err:
            print(f'An error occurred: {err}')

    def run_llama(self, prompt="Hello World", max_tokens = 1200):
        """
        Sends a prompt to the Llama model and fetches the generated output.

        This method sends a POST request to the Llama API with the specified prompt 
        and additional parameters. If the IBM access token is not available, it will 
        attempt to generate one.

        Args:
            prompt (str): The input prompt for the Llama model. Defaults to "Hello World".
            max_tokens (int): The maximum number of tokens to generate. Defaults to 1200.

        Returns:
            str: The generated text from the Llama model if the request is successful.

        Raises:
            HTTPError: If the HTTP request returns an unsuccessful status code.
            RequestException: If there are issues with the network request.
            Exception: For any other unexpected errors.
        """
        if not self.ibm_token:
            print("No IBM token found. Generating a new token...")
            self.get_ibm_access_token()

        body = {
            "input": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": 0.5,
                "decoding_method": "greedy",
                "repetition_penalty": 1.0,
            },
            "model_id": self.model_id,
            "project_id": self.project_id,
        }

        headers = {
            "Authorization": f"Bearer {self.ibm_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        try:
            response = requests.post(self.llama_url, headers=headers, json=body)
            response.raise_for_status()

            data = response.json()
            model_result = data['results'][0]['generated_text'].replace('**', '')
            return model_result

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except RequestException as req_err:
            print(f'Request error occurred: {req_err}')
        except Exception as err:
            print(f'An error occurred: {err}')

# # Uncomment this only to test the class methods locally. 
# if __name__ == "__main__":

#     # Initialize the LlamaConnector
#     client = LlamaConnector()

    # Example prompt
    # prompt = """Explain this code line by line.
    # # Function to generate Fibonacci series
    # def generate_fibonacci(n):
    #     # Initialize the first two terms
    #     a, b = 0, 1
    #     series = []
    #     for _ in range(n):
    #         series.append(a)
    #         a, b = b, a + b
    #     return series
    # print(generate_fibonacci(10))
    # """

    # # Get the generated text from the Llama model
    # print(client.run_llama(prompt,600))