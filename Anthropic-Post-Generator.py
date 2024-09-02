import streamlit as st
import json
import os
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from dotenv import load_dotenv
from datetime import datetime

# Initialize Anthropic client

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
# Initialize Anthropic client
anthropic = Anthropic(api_key=api_key)

JSON_FILE = 'social_media_posts.json'

# Function to generate content using Claude
def generate_content(platform, topic):
    try:
        prompt = f"""You are tasked with generating a social media post for a specific platform. Your goal is to create a concise, engaging post that adheres to the platform's best practices and captures the given topic.
You will be provided with the following information:
Social Media Platform : {platform}
Topic : {topic}

Guidelines for generating the social media post:
1. Tailor the post to the specific social media platform, considering character limits and typical post structures.
2. Focus on the given TOPIC, ensuring the content is relevant and informative.
4. Include appropriate hashtags, mentions, or emojis if relevant to the platform and topic.
5. Create a compelling hook or opening to grab the audience's attention.
6. If applicable, include a call-to-action that encourages engagement.

Your output should be the social media post only, without any additional explanation or information. Present your post within <post> tags.
Remember to keep the post concise and tailored to the specific platform's best practices. Do not exceed character limits or include elements that are not typical for the given platform.
        """
        
        message = anthropic.messages.create(
            model="claude-3-5-sonnet-20240620",
            system="you are a social media influencer",
            max_tokens=1300,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
    except Exception as e:
        st.error(f"Error generating content: {str(e)}")
        return None

# Function to save content to JSON file
def save_to_json(data):
    try:
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, 'r') as f:
                existing_data = json.load(f)
        else:
            existing_data = []
        
        existing_data.append(data)
        
        with open(JSON_FILE, 'w') as f:
            json.dump(existing_data, f, indent=4)
        return True
    except Exception as e:
        st.error(f"Error saving to JSON: {str(e)}")
        return False

# Streamlit UI
st.title("Social Media Post Generator")

# User input
platform = st.selectbox("Select social media platform", ["Twitter", "Instagram", "Facebook"])
topic = st.text_input("Enter the topic for your post")

if st.button("Generate Post"):
    if topic:
        with st.spinner("Generating post..."):
            generated_content = generate_content(platform, topic)
        
        if generated_content:
            st.subheader("Generated Post:")
            st.write(generated_content)
            
            # Save to JSON
            data = {
                "platform": platform,
                "topic": topic,
                "content": generated_content,
                "timestamp": datetime.now().isoformat()
            }
            
            if save_to_json(data):
                st.toast(f"Post saved to {JSON_FILE}")
            else:
                st.warning("Failed to save the post. Please try again.")
    else:
        st.warning("Please enter a topic for your post.")

# Display saved posts (excluding the last/oldest post)
st.write("---")
st.subheader("Previously Generated Posts")
try:
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r') as f:
            posts = json.load(f)
        
        if len(posts) > 1:  # Check if there's more than one post
            for post in reversed(posts[:-1]):  # Exclude the last post
                st.write(f"Platform: {post['platform']}")
                st.write(f"Topic: {post['topic']}")
                st.write(f"Content: {post['content']}")
                st.write(f"Timestamp: {post['timestamp']}")
                st.write("---")
        elif len(posts) == 1:
            st.info("Only one post available, which is not displayed as per request.")
        else:
            st.info("No posts generated yet.")
    else:
        st.info("No posts generated yet.")
except Exception as e:
    st.error(f"Error reading saved posts: {str(e)}")