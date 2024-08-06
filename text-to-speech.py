import streamlit as st
from pathlib import Path
import openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
api_key = os.getenv('api_key')
if api_key:
    openai.api_key = api_key
else:
    st.error("OpenAI API key must be set in the .env file.")
    st.stop()

def generate_speech(text):
    speech_file_path = Path('speech.mp3')
    try:
        # Create speech using OpenAI's API (Assuming api features are correct)
        speech_file_path = Path(__file__).parent / "speech.mp3"
        response = openai.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input="The quick brown fox jumped over the lazy dog."
        )

        # Save the response audio to a file
        with open(speech_file_path, 'wb') as f:
            f.write(response['audio'])
        return speech_file_path
    except Exception as e:
        st.error(f"Failed to generate speech: {e}")
        return None

def main():
    st.title("Text to Speech Converter")
  
    # User input
    user_input = st.text_area("Enter text you want converted to speech:", "The quick brown fox jumped over the lazy dog.")
    if st.button("Generate Speech"):
        speech_file = generate_speech(user_input)
        if speech_file:
            st.audio(str(speech_file), format='audio/mp3', start_time=0)

if __name__ == "__main__":
    main()