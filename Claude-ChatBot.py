"""
# Anthropic Claude Sonnet Chatbot

This is a Streamlit application that provides a conversational interface powered by Anthropic's Claude language models. Users can select from different Claude model versions and interact with the chatbot, with the conversation history being persisted in the session state.

## Key Features:
- **Model Selection**: Users can choose from different Claude model versions, each with its own capabilities and performance characteristics.
- **Chat History**: The application maintains a chat history, allowing users to review previous messages and responses.
- **Streaming Response**: The chatbot's responses are streamed to the user, providing a more natural and engaging interaction.
- **Token Usage and Cost Display**: The application displays the number of tokens used and the estimated cost for each response, based on the selected model.
- **Error Handling**: The application gracefully handles various errors, such as rate limits, connection issues, and API errors, and provides appropriate feedback to the user.

## Usage:
1. Ensure you have the necessary Anthropic API key set up in your Streamlit secrets.
2. Run the Streamlit application.
3. In the sidebar, select the desired Claude model and adjust the maximum tokens.
4. Start chatting with the Claude chatbot in the main content area.
5. The chat history and token/cost information will be displayed as the conversation progresses.

parag.jn@gmail.com
"""

import streamlit as st
import anthropic
from dotenv import load_dotenv
import os

load_dotenv()
# Initialize the Anthropic client
client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])       # antrhopic key

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Set page config
st.set_page_config(layout="wide", page_title="Anthropic Chatbot")

# Sidebar (currently empty)
st.sidebar.title("Chatbot Settings")

with st.sidebar:
    st.write("---")
    max_tokens = st.slider("Max Tokens",min_value=100,max_value=5000,value=100,step=10)
    model_choices = st.radio(
        "Select Model",
        ["None","Claude 3.5 Sonnet","Claude 3 Opus","Claude 3 Sonnet","Claude 3 Haiku"],
        index=0  # Default to Claude 3
    )

# set the model over here
    model_help_text = ""        # default message
    if model_choices == 'Claude 3.5 Sonnet':
        model = 'claude-3-5-sonnet-20240620'
        model_help_text = """-Most intelligent model<br>
-Text and image input<br>
-Text output<br>
-Training data : Aug 2024
"""
    elif model_choices == 'Claude 3 Opus':
        model = 'claude-3-opus-20240229'
        model_help_text = """-Powerful model for highly complex tasks<br>
-Text and image input<br> 
-Text output
-Training data : Aug 2023
"""
    elif model_choices == 'Claude 3 Sonnet':
        model = 'claude-3-sonnet-20240229'
        model_help_text = """-Balance of speed and intelligence<br>
-Text and image input<br>
-Text output<br>
-Training data : Aug 2023
"""
    elif model_choices == 'Claude 3 Haiku':
        model = 'claude-3-haiku-20240307'
        model_help_text = """-Fastest and most compact model<br>
-Text and image input<br> 
-Text output<br>
-Training data : Aug 2023
"""
    elif model_choices == 'None':
        model = 'none'

    st.write("---")
    st.markdown(model_help_text,unsafe_allow_html=True)

    # clear the screen by hitting this button
    clear_screen = st.button("Clear All")
    if clear_screen:
        st.session_state.messages = []  # Clear the messages
        st.rerun()

# Main content
st.title("ANTHROP\C Claude Sonnet Chatbot")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input for new message
if prompt := st.chat_input("What would you like to ask?"):
    try:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Prepare messages for API call
        api_messages = []
        try:
            for message in st.session_state.messages[-9:]:  # Keep last 9 messages for context
                if message["role"] in ["user", "assistant"]:
                    api_messages.append({"role": message["role"], "content": message["content"]})
        except IndexError as e:
            st.error(f"Error accessing message history: {str(e)}")
            api_messages = [{"role": "user", "content": prompt}]
        
        # Get AI response
        with st.chat_message("assistant"):
            tokens_used = 0
            cost = 0.0
            message_placeholder = st.empty()
            full_response = ""
            try:
                if model == 'none':
                    st.warning("Select a model to continue")
                    st.stop()
                else:
                    with client.messages.stream(
                        model=model,
                        max_tokens=max_tokens,
                        messages=api_messages
                    ) as stream:
                        for text in stream.text_stream:
                            full_response += text
                            tokens_used = client.count_tokens(full_response)
                            # Calculate cost based on the model
                            if model == 'claude-3-5-sonnet-20240620':
                                cost = tokens_used * 0.000003  # $0.003 per 1K tokens
                            elif model == 'claude-3-opus-20240229':
                                cost = tokens_used * 0.000015  # $0.015 per 1K tokens
                            elif model == 'claude-3-sonnet-20240229':
                                cost = tokens_used * 0.000003  # $0.003 per 1K tokens
                            elif model == 'claude-3-haiku-20240307':
                                cost = tokens_used * 0.0000005  # $0.0005 per 1K tokens
                            message_placeholder.markdown(full_response + "▌")
            except anthropic.RateLimitError as e:
                st.error(f"Rate Limit Error: {str(e)}")
                full_response = "I've reached my usage limit. Please wait a moment and try again."
            except anthropic.APIConnectionError as e:
                st.error(f"Connection Error: {str(e)}")
                full_response = "I'm having trouble connecting to the server. Please try again later."
            except anthropic.APIError as e:
                st.error(f"API Error: {str(e)}")
                full_response = "I apologize, but I encountered an error while processing your request."
            
            message_placeholder.markdown(full_response)
            # Display token count and cost after the response
            st.write("---")
            st.markdown(f'***:grey[Tokens used: {tokens_used} | Cost: ${cost:.6f}]***')
        
        # Add AI response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    except Exception as e:
        st.error(f"An error occurred while processing your request: {str(e)}")

# Display message count
# st.markdown(f"<p style='font-size: small;'>Messages: {len(st.session_state.messages)}/10</p>", unsafe_allow_html=True)

# Limit context to last 10 messages
st.session_state.messages = st.session_state.messages[-10:]
