import os
from openai import OpenAI
from dotenv import load_dotenv

class XAIConnector:
    """
    A class to handle connections and interactions with X.AI API
    """
    
    def __init__(self):
        """Initialize the XAI connector with API credentials from environment"""
        load_dotenv()
        self.api_key = os.getenv('X_API_KEY')
        self.base_url = os.getenv('X_API_BASEURL')
        
        if not self.api_key or not self.base_url:
            raise ValueError("Missing required environment variables: X_API_KEY or X_API_BASEURL")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def generate_completion(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generate a completion using the X.AI API
        
        Args:
            system_prompt (str): The system prompt to set context
            user_prompt (str): The user's input prompt
            
        Returns:
            str: The generated completion text
        """
        try:
            completion = self.client.chat.completions.create(
                model="grok-beta",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return completion.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating completion: {str(e)}")

def test_xai_connection():
    """Test the XAI connection and basic functionality"""
    try:
        # Initialize connector
        xai = XAIConnector()
        
        # Test prompt
        system_prompt = "You are Grok, a chatbot"
        user_prompt = "What is the meaning of life?"
        
        # Generate response
        response = xai.generate_completion(system_prompt, user_prompt)
        
        print("Connection Test Successful!")
        print("Test Response:", response)
        return True
        
    except Exception as e:
        print(f"Connection Test Failed: {str(e)}")
        return False

# Run test if file is executed directly
if __name__ == "__main__":
    test_xai_connection()