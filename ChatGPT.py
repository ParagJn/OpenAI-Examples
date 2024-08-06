#####
# Chat bot based on open ai's gpt model(s)
# requires an api key from openai. 
# parag.jn@gmail.com
####

import streamlit as st
import openai
import time
import json
import os
from datetime import datetime
from dotenv import load_dotenv

## Setting page config
st.set_page_config(
    page_title="Open Ai - Chatbot",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# A simple open-ai based chatbot with model choices!"
    },
) # end of page config

load_dotenv()  # Load the environment variables

def validate_api_key(api_key):
    """Validate the API key."""
    openai.api_key = api_key
    try:
        openai.Model.list()
        return True
    except openai.error.AuthenticationError:
        return False

def get_valid_api_key():
    """Prompt the user to input a valid API key until a valid one is provided."""
    api_key = st.text_input("Please enter a valid OpenAI API key:", type="password")
    if st.button("Validate"):
        if validate_api_key(api_key):
            st.success("API key is valid!")
            return api_key
        else:
            st.error("Invalid API key. Please try again.")
            st.stop()  # Stop the script until a valid API key is provided

# Get or validate the API key
API_KEY = os.environ.get("api_key")
if not API_KEY or not validate_api_key(API_KEY):
    API_KEY = get_valid_api_key()
else:
    openai.api_key = API_KEY

st.title("GPT Chatbot") # page title

# Ensure the feedback directory exists
feedback_dir = os.path.join("model_responses", "feedback")
os.makedirs(feedback_dir, exist_ok=True)

def generate_response(model, messages, temperature, agent_type = "Friendly Chatbot"):
    try:
        if agent_type == "Expert Programmer":
            messages.insert(0, {"role": "system", "content": "You are an expert programmer. Provide detailed and advanced programming help."})
        elif agent_type == "Friendly Chatbot":
            messages.insert(0, {"role": "system", "content": "You are a helpful assistant. Provide friendly and useful responses."})
        elif agent_type == "Travel Agent":
            messages.insert(0, {"role": "system", "content": "You are a expert travel planner. Provide friendly best possible itinerary to make travel as enjoyable as possible."})

        response = openai.ChatCompletion.create(
            model=f"{model}",
            messages=messages,
            max_tokens=3500, # Reasonable token limit to optimize cost and performance
            n=1,
            stop=None,
            temperature=temperature, # Adjust temperature for better variability
        )
        return response.choices[0]['message']['content']
    except openai.error.OpenAIError as e:
        # Log the error and inform the user
        st.error(f"There was an API error: {e}")
    except Exception as e:
        # Catch-all for other exceptions
        st.error(f"An unexpected error occurred: {e}")
    return None

def log_feedback(user_input, response):
    feedback_entry = {
        "timestamp": str(datetime.now()),
        "query": user_input,
        "response": response
    }
    feedback_file_path = os.path.join(feedback_dir, "feedback.json")
    try:
        with open(feedback_file_path, "a") as file:
            file.write(json.dumps(feedback_entry) + "\n")
        st.toast(f"Oops !! Sorry, the response was not as per your liking. \nWe have registered the feedback for further improvements.")
    except Exception as e:
        st.error(f"Failed to log feedback: {e}")

def main():
    model_choices = ['none', 'gpt-4', 'gpt-4o', 'gpt-4-turbo', 'gpt-4o-mini', 'gpt-3.5-turbo']
    # put the side bar
    with st.sidebar:
        model_selection = st.radio("Select the model", model_choices, index=0)

        # creativity slider
        creativity_value = st.slider("Response Type - Focussed to creative", min_value=0.1, max_value=1.0, step=0.1, value=0.5)

        #agent type
        agent_type = st.selectbox("Select your agent",options=['Friendly Chatbot','Expert Programmer','Travel Agent'])
        st.write(agent_type)

        # Clear history button
        if st.button("Clear History"):
            st.session_state.user_input = ""
            st.session_state.response = ""
            st.session_state.history = []
            st.rerun() # Rerun to refresh the chat session

    if "user_input" not in st.session_state:
        st.session_state.user_input = ""
    if "response" not in st.session_state:
        st.session_state.response = ""
    if "feedback" not in st.session_state:
        st.session_state.feedback = None
    if "history" not in st.session_state:
        st.session_state.history = []

    st.write("Hello! I am a chatbot powered by OpenAI's GPT-4. How can I help you today?")
    st.write("---")
    
    st.session_state.user_input = st.text_input("You:", st.session_state.user_input, max_chars=300,)

    if st.button("Send") and st.session_state.user_input:
        if model_selection != 'none':
            with st.spinner("⌛ Generating response..."):
                # Create the context from history
                messages = [{"role": "assistant" if i % 2 else "user", "content": message} for i, message in enumerate(st.session_state.history)]
                messages.append({"role": "user", "content": st.session_state.user_input})

                st.session_state.response = generate_response(model_selection, messages, creativity_value,agent_type)
                if st.session_state.response:
                    # Update history with new response
                    st.session_state.history.extend([
                        st.session_state.user_input,
                        st.session_state.response
                    ])
                    # Keep only the last 5 interactions (each interaction consists of user and assistant message)
                    st.session_state.history = st.session_state.history[-10:]

                    def stream_data():
                        for word in st.session_state.response.split(" "):
                            yield word + " "
                            time.sleep(0.02)

                    st.write(f"**You:** {st.session_state.user_input}")
                    st.write("**Bot:**")
                    st.write_stream((stream_data()))
                    st.write("---")
                    st.session_state.feedback = "### Did you find the response helpful?"
        else:
            st.warning("Select a model to continue.. ")
            st.stop()
    
if __name__ == "__main__":
    main()