# A simple class file to connect to OpenAI model hosted on Azure
# Parag Jain. 

import os
import logging
from dotenv import load_dotenv
from openai import AzureOpenAI
from App_Logger import get_logger

logger = get_logger()


class AzureAIConnectionError(Exception):
    """Custom exception for Azure AI connection errors."""
    pass

class AzureAIConnection:
    def __init__(self):
        """
        AzureAIConnection class.
        Load environment variables and create an instance of the AzureOpenAI client.
        Requires the following environment variables:
        - AZURE_OPENAI_VERSION
        - AZURE_OPENAI_KEY
        - AZURE_OPENAI_BASE
        - AZURE_OPENAI_DEPLOYMENT_NAME
        """
        load_dotenv()
        try:
            self.client = self._initialize_client()
            self.deployment_name = self._get_env_variable("AZURE_OPENAI_DEPLOYMENT_NAME")
        except Exception as e:
            logger.exception(f"Error during Azure AI connection initialization: {e}")
            raise AzureAIConnectionError(e)

    def _get_env_variable(self, var_name: str) -> str:
        value = os.getenv(var_name)
        if not value:
            logger.exception(f"Missing environment variable: {var_name}")
            raise AzureAIConnectionError(f"Missing environment variable: {var_name}")
        return value

    def _initialize_client(self) -> AzureOpenAI:
        api_key = self._get_env_variable("AZURE_OPENAI_KEY")
        api_version = self._get_env_variable("AZURE_OPENAI_VERSION")
        azure_endpoint = self._get_env_variable("AZURE_OPENAI_BASE")
        logger.info("Azure AI connection initialized successfully")
        return AzureOpenAI(api_key=api_key, api_version=api_version, azure_endpoint=azure_endpoint)

    def get_client(self) -> AzureOpenAI:
        """
        Return the AzureOpenAI client instance.
        Returns:
            AzureOpenAI: The client instance for Azure OpenAI.
        """
        if not self.client:
            raise AzureAIConnectionError("The Azure OpenAI client is not initialized.")
        return self.client

    def get_deployment_name(self) -> str:
        """
        Return the Azure deployment name.
        Returns:
            str: The deployment name for Azure OpenAI.
        """
        if not self.deployment_name:
            raise AzureAIConnectionError("The deployment name is not initialized.")
        return self.deployment_name

# ## Test the class file. Uncomment this block if you want to test the class file by running this file.
# if __name__ == "__main__":
#     try:
#         azure_ai_connection = AzureAIConnection()
#         client = azure_ai_connection.get_client()
#         deployment_name = azure_ai_connection.get_deployment_name()
        
#         response = client.chat.completions.create(
#             model=deployment_name,
#             messages=[
#                 {"role": "system", "content": "You are an helpful assistant"},
#                 {"role": "user", "content": "hello world"},
#                 {"role": "user", "content": "Write an long essay on history of the world"}
#             ],
#             max_tokens=2200
#         )
#         output = response.choices[0].message.content.strip()
        
#         print("Response from Azure OpenAI:", output)
#     except AzureAIConnectionError as e:
#         logger.error(f"Failed to connect to Azure OpenAI: {e}")
#     except Exception as e:
#         logger.error(f"An error occurred: {e}")