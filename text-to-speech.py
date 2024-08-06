## Requires open api key set as environment variable
## for windows, set it at environment level
## for linux/mac, use export OPEN_API_KEY = 'Your-key-here'

# this program will conver the given text into a realistic sounding voice. 

import streamlit as st
from pathlib import Path
import openai
from dotenv import load_dotenv

st.set_page_config(
    page_title="Open Ai - Chatbot",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# An app that can convert text to speech using OpenAI's tts Model"
    },
)

# Load environment variables from .env file
load_dotenv()

def generate_speech(text,voice="alloy"):
    # speech_file_path = Path('speech.mp3')
    # Create speech using OpenAI's API (Assuming api features are correct)
    speech_file_path = Path(__file__).parent / "speech.mp3"
    response = openai.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text  # Use the text provided by the user
    )
    # Save the response audio to a file
    with open(speech_file_path, 'wb') as f:
        f.write(response.content)
        return speech_file_path

def main():
    st.title("Text to Speech Converter")

    voices = ['alloy', 'echo', 'fable', 'onyx', 'nova','shimmer']
    with st.sidebar:
        selected_voice = st.radio("Select the voice to generate speech",options=voices,index=1)
  
    # User input
    user_input = st.text_area("Enter text you want converted to speech:", "The quick brown fox jumped over the lazy dog.")
    if st.button("Generate Speech"):
        speech_file = generate_speech(user_input,selected_voice)
        if speech_file:
            st.audio(str(speech_file), format='audio/mp3', start_time=0)

if __name__ == "__main__":
    main()
