# Using microsoft's library to convert docx into markdown for further processing with llms

from markitdown import MarkItDown
from openai import OpenAI
import os
from dotenv import load_dotenv  

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

md = MarkItDown(llm_client=client, llm_model="gpt-4o")

def extract_process_overview(doc_path):
    result = md.convert(doc_path)
    process_overview_start = result.text_content.find("PROCESS OVERVIEW")
    if process_overview_start != -1:
        process_overview_end = result.text_content.find("\n", process_overview_start)
        next_paragraphs_start = process_overview_end + 1
        next_paragraphs_end = result.text_content.find("\n\n", next_paragraphs_start)
        next_paragraphs = result.text_content[next_paragraphs_start:next_paragraphs_end].strip()
        print(f"Process Overview: {result.text_content[process_overview_start:process_overview_end].strip()}")
        print(f"Next 2 Paragraphs: {next_paragraphs}")
    else:
        print("PROCESS OVERVIEW not found in the document")

extract_process_overview('/Users/paragjain/Downloads/Aerospace_order to cash_BWL_Document_1.docx')
extract_process_overview('/Users/paragjain/Downloads/OTC_Credit Memo Processing (1EZ).docx')
