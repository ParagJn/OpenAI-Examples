#############
# PDD (Business Process Design Document Generator)
# This is a ultra-lightweight application to demonstrate the use of OpenAI's GPT-4 model for generating Business Process Design Documents (PDD) based on user's inputs. 
# The application allows users to upload a document or an image, which is then processed to generate a design document. 
# The application also generates a business process model and allows users to download the BPMN format, that can modified using BPMN editors available. 
# Parag Jain
#############

import streamlit as st
from markitdown import MarkItDown, FileConversionException
import re
import os
import tiktoken
from AzureAIConnection import AzureAIConnection
from PromptGenerator import PromptGenerator
from BPMN_Functions import render_bpmn_viewer
from App_Logger import get_logger
from llama_connector import LlamaConnector
from Image_Convertor import ImageConverter

# Initialize logger
logger = get_logger()
logger.info("Application Started")

class ProcessDesignGenerator:
    """
    A class to handle the generation of process design documents and BPMN diagrams.
    """

    def __init__(self):
        """
        Initialize the ProcessDesignGenerator with Azure AI connection and client.
        """
        self.azure_connection = AzureAIConnection()
        self.client = self.azure_connection.get_client()
        self.deployment_name = self.azure_connection.get_deployment_name()

    def extract_sections(self, text, sections)->str:
        """
        Extract sections from the provided text based on the section names.

        :param text: str: The text to extract sections from.
        :param sections: list: A list of section names to extract.
        :return: str: Extracted sections as a string.
        """
        extracted = {}
        for section in sections:
            pattern = re.compile(rf"{section}.*?(?=\n#|$)", re.DOTALL)
            match = pattern.search(text)
            if match:
                extracted[section] = match.group().strip()
        return str(extracted)

    def generate_response(self, messages, max_tokens, deployment_name)->str:
        """
        Generate a response from the Azure AI client.

        :param messages: list: A list of messages to send to the AI client.
        :param max_tokens: int: The maximum number of tokens for the response.
        :param deployment_name: str: The deployment name of the AI model.
        :return: response: The response from the AI client.
        """
        response = self.client.chat.completions.create(
            model=deployment_name,
            messages=messages,
            max_tokens=max_tokens
        )
        return response

    def crosscheck_response(self, run_crosscheck=False, context="", generated_text="")->str:
        """
        Validate the generated content by running a cross-check.

        :param run_crosscheck: bool: Whether to run the cross-check.
        :param context: str: The SAP business context.
        :param generated_text: str: The generated text to validate.
        :return: str: The cross-check response.
        """
        if run_crosscheck:
            logger.info("Running the cross-check on the generated content")
            prompt = f"""
                You are an expert in SAP, possessing in-depth knowledge of SAP business processes, systems, and best practices.
                Your task is to critically evaluate a document and highlight negative aspects based on two key inputs:
                
                1. **SAP Business Context:** Analyze how the document aligns with the specific SAP business context provided.
                2. **Document Text:** Evaluate this text in terms of accuracy, relevance to the context, and adherence to SAP standards and best practices.
                
                After analyzing the SAP Business context & Document text, Only include these in your response. 
                - List 3 critical areas for improvement in bullet points.

                **Formatting Requirements:**
                - Enclose your entire response within `<Validate Text>` tags.
                - Use precise, succinct language for all points.
                
                **Inputs:**
                - **SAP Business Context:** {context}
                - **Document Text:** {generated_text}
            """
            llama_client = LlamaConnector()
            crosscheck_response = llama_client.run_llama(prompt)
            logger.info("Received the cross-check response from llama model")
            return crosscheck_response
        else:
            logger.info("Crosscheck on the generated content not requested")
            return None

    def calculate_tokens_gpt4(self, messages, model="gpt-4o")->int:
        """
        Calculate the total token count for a GPT-4 completion request.

        :param messages: list: A list of messages to send to the AI client.
        :param model: str: The model name.
        :return: int: The total token count.
        """
        encoding = tiktoken.encoding_for_model(model)
        total_tokens = 0
        for message in messages:
            total_tokens += 4  # Each message has a role and metadata overhead
            total_tokens += len(encoding.encode(message["content"]))
        total_tokens += 2  # Add 2 tokens for the stop sequence
        return total_tokens

    def improve_content_with_feedback(self, messages, negative_feedback, max_tokens, deployment_name, run_improvement=False)->str:
        """
        Improve the original content based on the negative feedback.

        :param messages: list: A list of messages to send to the AI client.
        :param negative_feedback: str: The negative feedback to improve the content.
        :param max_tokens: int: The maximum number of tokens for the response.
        :param deployment_name: str: The deployment name of the AI model.
        :param run_improvement: bool: Whether to run the improvement process.
        :return: str: The improved content.
        """
        if run_improvement:
            logger.info("Running the improvement process based on negative feedback")
            prompt = """Update the SAP design document based on inaccuracies or gaps are found based on the feedback. 
            Add content to relevant sections without deleting or altering any existing content unnecessarily.
            """
            messages.append({"role": "user", "content": f"{prompt}:\n{negative_feedback}"})
            improved_response = self.generate_response(messages, max_tokens, deployment_name)
            improved_content = improved_response.choices[0].message.content.strip()
            logger.info("Improvement process completed")
            return improved_content
        else:
            logger.info("Improvement process not requested")
            return None

    def handle_bpmn_output(self, output)->str:
        """
        Extract and render BPMN content from the output.

        :param output: str: The output containing BPMN content.
        :return: str: The cleaned output without BPMN content.
        """
        output_cleaned = re.sub(r"<BPMN Script>.*?</BPMN Script>", "", output, flags=re.DOTALL)
        output_cleaned = re.sub(r"<.*?>", "", output_cleaned)
        
        bpmn_pattern = re.compile(r"<BPMN Script>(.*?)</BPMN Script>", re.DOTALL)
        bpmn_match = bpmn_pattern.search(output)
        if bpmn_match:
            logger.info("BPMN output found in the response.")
            bpmn_content = bpmn_match.group(1).strip()
            
            xml_start = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
            xml_end = "</definitions>"
            start_index = bpmn_content.find(xml_start)
            end_index = bpmn_content.rfind(xml_end) + len(xml_end)
            if start_index != -1 and end_index != -1 and start_index < end_index:
                bpmn_content = bpmn_content[start_index:end_index]
            else:
                bpmn_content = f"{xml_start}\n{xml_end}"
            
            st.components.v1.html(render_bpmn_viewer(bpmn_content), height=800)
            with open("BPMN_Output.bpmn", "w") as xml_file:
                xml_file.write(bpmn_content)
            
            with open("BPMN_Output.bpmn", "r") as file:
                st.download_button(
                    label="Download BPMN Format File",
                    data=file,
                    file_name="BPMN_Output.bpmn",
                    mime="application/xml"
                )
            logger.info("BPMN handling complete")
        else:
            logger.warning("No BPMN output found in the response.")
        
        return output_cleaned

    def process_uploaded_file(self, filename):
        """
        Process the uploaded file to generate the PDD.

        :param filename: str: The name of the uploaded file.
        """
        try:
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                logger.info("Image is uploaded and getting converted to text")
                with st.sidebar:
                    st.image(filename, caption="Your Image", use_container_width=True)
                converter = ImageConverter()
                result = converter.convert(
                    filename,
                    llm_client=self.client,
                    llm_model=self.deployment_name,
                    llm_prompt="Describe the given image in detail"
                )
                logger.info("Image read is complete, sending it for parsing with Prompt")
                generator = PromptGenerator(result.text_content, "Markdown")
                prompt = generator.generate()
                logger.info("Prompt generation is complete")

            elif filename.endswith('.docx'):
                md = MarkItDown(llm_client=self.client, llm_model=self.deployment_name)
                logger.info("Document is uploaded and getting converted to text")
                result = md.convert(filename)
                # Extract sections from the document is hard coded for now, TODO: need to be updated based on the document
                sections = ["# PROCESS OVERVIEW:", "### Summary", "### S4/HANA Features & Functionalities"]
                extracted_content = self.extract_sections(result.text_content, sections)

                if extracted_content:
                    st.write("Extracted sections from the document:")
                    st.json(extracted_content, expanded=False)
                else:
                    logger.warning("Invalid document, no content was extracted")
                    st.warning("No sections were extracted from the document. Add more details to the document or upload a new document to generate the PDD")
                    os.remove(filename)
                    st.stop()
                logger.info("Text is extracted, sending it for prompt generation")
                generator = PromptGenerator(extracted_content, "Markdown")
                prompt = generator.generate()
                logger.info("Prompt generation is complete")

            if prompt:
                logger.info("Sending the prompt to Azure AI for LLM response")
                st.write("Generating Process Design. Please wait...")
                messages = [
                    {"role": "system", "content": "You are an expert in SAP Processes and Documentation"},
                    {"role": "user", "content": prompt}
                ]
                try:
                    response = self.generate_response(messages=messages, max_tokens=1600, deployment_name=self.deployment_name)
                    output = response.choices[0].message.content.strip()
                except Exception as e:
                    logger.error(f"Error generating response: {str(e)}")
                    st.error(f"An error occurred while generating the response: {str(e)}")
                    st.stop()

                token_size = [
                    {"role": "system", "content": "You are an expert in SAP Processes and Documentation"},
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": output}
                ]
                total_tokens = self.calculate_tokens_gpt4(token_size)
                logger.info(f"Tokens utilized to generate content (input+output) are: {total_tokens}")

                logger.info("LLM response is generated, cleaning the content and displaying on screen")
                output_cleaned = re.sub(r"<.*?>", "", output)
                st.write("Process Design Generated:")
                st.write(output_cleaned)
                #TODO: Add the functions to validate the generated content using llama model and then, give the result back to OpenAI model. 
                # Refactor the observations and re-generate the content. 
                logger.info("Generating BPMN content using the generated output")
                bpmn_generator = PromptGenerator(output, "BPMN")
                bpmn_prompt = bpmn_generator.generate()
                messages = [
                    {"role": "system", "content": "You are an expert in generating BPMN 2.0 scripts"},
                    {"role": "user", "content": bpmn_prompt}
                ]
                try:
                    bpmn_output = self.generate_response(messages=messages, max_tokens=2800, deployment_name='gpt-4o')
                    logger.info("BPMN content is generated, handling the output")
                    bpmn_output = bpmn_output.choices[0].message.content.strip().replace("```", "")

                    bpmn_token_size = [
                        {"role": "system", "content": "You are an expert in generating BPMN 2.0 scripts"},
                        {"role": "user", "content": bpmn_prompt},
                        {"role": "user", "content": bpmn_output}
                    ]
                    logger.info(f"Tokens utilized for BPMN (input+output) are: {self.calculate_tokens_gpt4(bpmn_token_size)}")
                    bpmn_cleaned_output = self.handle_bpmn_output(bpmn_output)
                    logger.info("BPMN output is displayed, All done!")
                except Exception as e:
                    logger.error(f"Error generating BPMN response: {str(e)}")
                    st.error(f"An error occurred while generating the BPMN response: {str(e)}")
                    st.stop()

            os.remove(filename)
            logger.info("File clean up complete, this is the end of the process")
        except FileConversionException as fce:
            logger.fatal(f"Error observed during file conversion. Error message {str(fce)}")
            st.error(f"File conversion error: {str(fce)}")
        except Exception as e:
            logger.fatal(f"Unknown error observed. Error message {str(e)}")
            st.error(f"An error occurred: {str(e)}")

# Streamlit UI Page configuration
st.set_page_config(layout="wide",
                       page_icon="🧠",
                       page_title="Generate Business PDD",
                       initial_sidebar_state="expanded")

# Sidebar Content
with st.sidebar:
    st.title("Input Options")
    file_type = st.radio("Upload File", ["Document", "Image"])

# Main content to start the program execution
st.title("Business Process Design Generator")

# Initialize the ProcessDocumentationGenerator
pdd = ProcessDesignGenerator()

# File uploader logic
if file_type == "Document":
    uploaded_file = st.file_uploader("Upload a document", type=['docx'])
else:
    uploaded_file = st.file_uploader("Upload an image", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Process the uploaded file to generate the PDD
    pdd.process_uploaded_file(uploaded_file.name)