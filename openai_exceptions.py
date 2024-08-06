"""
Exception Overview:
This module defines a custom exception `InvalidAPIKeyError` for handling cases where the OpenAI API key is 
invalid. This exception provides a descriptive error message to help diagnose issues with API key authentication.

Custom Exception:
- InvalidAPIKeyError: Raised when the provided OpenAI API key is invalid.

Possible Exceptions from OpenAI API:
- openai.error.InvalidRequestError: Raised when the request to the OpenAI API is invalid.
- openai.error.AuthenticationError: Raised when authentication with the OpenAI API fails.
- openai.error.PermissionError: Raised when permissions are insufficient to access a particular endpoint.
- openai.error.RateLimitError: Raised when API request frequency exceeds the usage limit.
- openai.error.APIConnectionError: Raised when there is a network problem connecting to the OpenAI API.
- openai.error.APIError: A generic error raised for server-side issues in the OpenAI API.

Dependencies:
- openai

Author: parag.jn@gmail.com
Date: August 2024
"""

class InvalidAPIKeyError(Exception):
    """Exception raised for invalid API keys."""
    def __init__(self, message="The provided OpenAI API key is invalid."):
        self.message = message
        super().__init__(self.message)