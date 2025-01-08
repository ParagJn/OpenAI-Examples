# Using microsoft's library to convert docx into markdown for further processing with llms

from markitdown import MarkItDown
from openai import OpenAI
import os
from dotenv import load_dotenv  

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

md = MarkItDown(llm_client=client, llm_model="gpt-4o")
result = md.convert("/Users/paragjain/Downloads/Diwali.pdf")

print(result)
