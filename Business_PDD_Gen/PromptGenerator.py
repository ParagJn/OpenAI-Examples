# Prompt-Generator
# 
# A class to generate prompts based on the provided text and type.
# 
class PromptGenerator:
    def __init__(self, text="", prompt_type=None):
        """
        Initialize the PromptGenerator class.

        :param text: str: The text to generate the prompt (mandatory, defaults to an empty string).
        :param prompt_type: str: The type of prompt to generate (optional, e.g., "Markdown" or "GeneratePDD").
        """
        if not isinstance(text, str):
            raise ValueError("The 'text' parameter must be a string.")
        self.text = text
        self.prompt_type = prompt_type

    def generate(self):
        """
        Generate a prompt based on the initialized text and type.

        :return: str: The generated prompt.
        """
        if self.prompt_type == "Markdown":
            return f"""You are being given a text as below:
    {self.text}.
You need to first analyze the given text and determine whether it is related to SAP processes or functions. 
If the text is NOT related to SAP, output ONLY the following:
<NO Content>
The Input provided is not relevant to SAP. Hence, no content can be generated. Please try again with a different document or image
</NO Content>

Only if the text is relevant to SAP functions or processes, continue with the step & instructions below. 

First Step - Identify the SAP Industry and display as <Identified Industry>
Second Step - Identify the process name and display as <Identified Process Name>
Third Step - Identify the key process flows and display only the names of the process flows as <Identified Process Flows>
Fourth Step - Generate a technical process design using 800 to 1000 words for each of step identified in  <Identified Process Flows>.
Use Tag <Fourth Step> to enclose the content. 

Follow these instructions to accurately generate the design content. 
   - Build the technical contents for <Identified Process Name> using <Identified Process Flows>. Give a summary with <summary> tag and a detailed design using <design> Tag.
   Where applicable, include references to S4/HANA and/or Fiori Apps and functionalities that could enhance the documentation. 
   - Tailor all content strictly to the information for industry <Identified Industry>
   - Suggest relevant Fiori apps that could be used to execute or monitor the process steps.
   - Use SAP terminology and best practices consistently.
"""
        elif self.prompt_type == "BPMN":
            return f"""Identify the key process names provided in the text: {self.text} enclosed within <design> and </design> tags, 
            Then using the process names, generate a BPMN 2.0 XML script that:
Includes valid BPMN headers with necessary namespaces (xmlns, xmlns:xsi, xmlns:bpmndi, xmlns:omgdc, xmlns:omgdi).
Contains properly connected flow elements (<startEvent>, <task>, <endEvent>) and sequence flows with valid sourceRef and targetRef.
Follow BPMN 2.0.2 XML standards.
Ensure every opening tag has a matching and correctly placed closing tag.
Avoid any structural mismatches.
Represents a linear business process from start to end, with tasks clearly named based on the provided flow description.
Optionally includes diagram interchange elements (<bpmndi:BPMNDiagram>) for visualization. These should define shapes and edges for each element in the process.
Ensure that the generated XML is well-formed, readable, and compatible with BPMN modeling tools.
Use <BPMN Script> tag to enclose the script.
Do NOT add any summary or additional content to the script. Only include the BPMN XML script.
"""
        elif self.prompt_type is None:
            raise ValueError("No prompt was provided...")
        
#TODO: Implement the prompt generation for different types of input files.
#TODO: Implement prompt to generate the PDD documentation