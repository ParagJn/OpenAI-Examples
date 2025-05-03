# A simple chatgpt based chatbot. 
# Added o1-mini model to this. 

import streamlit as st
import time
import json
import os
from datetime import datetime
from openai_client import OpenAIClient

# Initialize OpenAI Client
openai_client_obj = OpenAIClient()
client = openai_client_obj.get_client()

log_file_path = os.path.join("model_responses", "activities.json")

def log_activity(input_query, output_message):
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "inputQuery": input_query,
        "outputMessage": output_message
    }
    try:
        if os.path.exists(log_file_path):
            with open(log_file_path, "r") as file:
                logs = json.load(file)
        else:
            logs = []
        logs.append(log_entry)
        with open(log_file_path, "w") as file:
            json.dump(logs, file, indent=2)
    except Exception as e:
        st.error(f"Failed to log activity: {e}")

# Streamlit application setup
st.set_page_config(
    page_title="Open Ai - Chatbot",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# A simple open-ai based chatbot with model choices!"
    },
)

st.title("GPT Chatbot")
feedback_dir = os.path.join("model_responses", "feedback")
os.makedirs(feedback_dir, exist_ok=True)

def generate_response(model, messages, temperature, max_tokens, agent_type="Friendly Chatbot"):
    expert_programmer_prepend_message = """<context>
You are an expert programming Al assistant who prioritizes minimalist, efficient code. You plan before coding, write idiomatic solutions, seek clarification when needed, and accept user preferences even if suboptimal. </context>
<planning_rules>
- Create 3-step numbered plans before coding
- Optimize for minimal code and overhead </planning_rules>
< format_rules>
- Use code blocks for simple tasks and add codetext
- Split long code into sections
- Create artifacts for file-level tasks
- Keep responses brief but complete </format_rules>
OUTPUT: Create responses following these rules.
Focus on minimal, efficient solutions while maintaining a helpful, concise style.
"""
    try:
        prepended_message = {
            "Expert Programmer": f"{expert_programmer_prepend_message}",
            "Friendly Chatbot": "You are a helpful assistant.",
            "Travel Agent": "You are a travel planner.",
            "Prompt Expert": "You are an expert prompt engineer"
        }.get(agent_type, "You are a helpful assistant.")

        if model in ['o1-mini', 'o3-mini']:
            # Prepend system message according to agent type
            messages.insert(0, {"role": "user", "content": prepended_message})
            response = client.chat.completions.create(
                model=model,
                messages=messages,
            )
        else:
            # Prepend system message according to agent type
            messages.insert(0, {"role": "system", "content": prepended_message})
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                n=1,
                stop=None,
                temperature=temperature,
            )
        return response.choices[0].message.content
    except Exception as e:
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
    model_choices = ['none', 'gpt-4', 'gpt-4o', 'gpt-4-turbo', 'gpt-4o-mini', 'gpt-3.5-turbo','o1-mini','o3-mini']
    # put the side bar
    with st.sidebar:
        model_selection = st.radio("Select the model", model_choices, index=0)

        # creativity slider
        creativity_value = st.slider("Response Type - Focussed to creative", min_value=0.1, max_value=1.0, step=0.1, value=0.5)

        # agent type
        agent_type = st.selectbox("Select your agent", options=['Friendly Chatbot', 'Expert Programmer', 'Travel Agent','Prompt Expert'])

        # max tokens
        max_tokens = st.text_input("Enter max tokens. ",max_chars=5,value=100,help="Use wisely to manage costs")

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
    
    st.session_state.user_input = st.text_input("Enter your query and press Enter:", st.session_state.user_input, max_chars=300)

    if st.button("Send") and st.session_state.user_input:
        if model_selection != 'none':
            with st.spinner("⌛ Generating response...", show_time=True):
                # Create the context from history
                if model_selection in ['o1-mini', 'o3-mini']:
                    messages = [{"role": "user", "content": message} for i, message in enumerate(st.session_state.history)]
                else:
                    messages = [{"role": "assistant" if i % 2 else "user", "content": message} for i, message in enumerate(st.session_state.history)]
                
                messages.append({"role": "user", "content": st.session_state.user_input})
                st.session_state.response = generate_response(model_selection, messages, creativity_value, int(max_tokens), agent_type)
                if st.session_state.response:
                    # Log the activity
                    log_activity(st.session_state.user_input, st.session_state.response)
                    # Update history with new response
                    st.session_state.history.extend([
                        st.session_state.user_input,
                        st.session_state.response
                    ])
                    # Keep only the last 5 interactions (each interaction consists of user and assistant message)
                    st.session_state.history = st.session_state.history[-10:]

                    def stream_data():
                        response_text = ""
                        placeholder = st.empty()
                        for word in st.session_state.response.split(" "):
                            response_text += word + " "
                            placeholder.markdown(f"**Bot:** {response_text}")
                            time.sleep(0.02)

                    st.write(f"**You:** {st.session_state.user_input}")
                    stream_data()
                    st.write("---")
                    st.session_state.user_input = ""
                    # st.session_state.feedback = "### Did you find the response helpful?"
        else:
            st.warning("Select a model to continue.. ")
            st.stop()

if __name__ == "__main__":
    main()
