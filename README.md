# OpenAI-Examples

Various examples of simple application that uses openai framework to generate the content. 
Following are the applications created. 

1. ChatGPT - this is my version of the chatgpt; The app provides an option to select the list of openai models.
2. Content summarizer - this applcation takes pdf document as an input and generates the summary of the contents
3. Social Media Post Creator - this applicaiton takes an image as an input and generates social media friendly posts.

All the appliation will require a .env file in root folder for access to openai api
create a .env file as below:

api_key = 'YOUR-API-KEY-OVER-HERE'


Additionally, the application(s) use streamlit UI framework to display the contents on the web-browser.  
visit streamlit.io to know more about this UI framework

Note : 

There are 2 version of openai connector class. 

1. openai_client - this uses the latest version of openai = 1.39
2. openai_connector - this uses older version of openai = 0.28. I have maintained this version for error management and compatibility with my older programs. 
