import streamlit as st
import json
import os
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from dotenv import load_dotenv
from datetime import datetime

# Initialize Anthropic client
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
anthropic = Anthropic(api_key=api_key)

JSON_FILE = 'social_media_posts.json'
CACHE_FILE = 'cache.json'

# Load cache
def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save cache
def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=4)

cache = load_cache()

# Function to generate content using Claude
def generate_content(platform, topic, force_generate=False):
    cache_key = f"{platform}_{topic}"
    if cache_key in cache and not force_generate:
        return cache[cache_key]

    try:
        char_limits = {"Twitter": 280, "Instagram": 2200, "Facebook": 63206}
        prompt = f"""You are tasked with generating a social media post for a specific platform. Your goal is to create a concise, engaging post that adheres to the platform's best practices and captures the given topic.
You will be provided with the following information:
Social Media Platform : {platform}
Topic : {topic}

Guidelines for generating the social media post:
1. Tailor the post to the specific social media platform, considering character limits and typical post structures.
2. Focus on the given TOPIC, ensuring the content is relevant and informative.
3. Use a friendly and conversational tone to engage the audience.
4. Include appropriate hashtags, mentions, or emojis if relevant to the platform and topic.
5. Create a compelling hook or opening to grab the audience's attention.
6. If applicable, include a call-to-action that encourages engagement.
7. Ensure the post is visually appealing if the platform supports media (e.g., images, videos).
8. Make sure the post is very close to the character limit for {platform}, which is {char_limits[platform]} characters.

Examples:
- Twitter: "Excited to share our latest update on {topic}! 🚀 #Innovation #TechNews"
- Instagram: "Discover the beauty of {topic} 🌸✨ #NatureLovers #Photography"
- Facebook: "Join the conversation about {topic} and share your thoughts! 💬 #Community #Discussion"

Your output should be the social media post only, without any additional explanation or information. Present your post within <post> tags.
Remember to keep the post concise and tailored to the specific platform's best practices. Do not exceed character limits or include elements that are not typical for the
given platform.
        """
        
        message = anthropic.messages.create(
            model="claude-3-5-sonnet-20240620",
            system="You are an expert content generation for social media",
            max_tokens=600,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        content = message.content[0].text
        cache[cache_key] = content
        save_cache(cache)
        return content
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

# Character limit display
char_limits = {"Twitter": 280, "Instagram": 2200, "Facebook": 63206}
if platform in char_limits:
    st.write(f"Character limit for {platform}: {char_limits[platform]}")

if st.button("Generate Post", key="generate_post", help="Click to generate a social media post based on the selected platform and topic."):
    if not topic:
        st.warning("Please enter a topic for your post.")
    elif len(topic) > char_limits[platform]:
        st.warning(f"Topic exceeds character limit for {platform}. Please shorten your topic.")
    else:
        with st.spinner("Generating post..."):
            generated_content = generate_content(platform, topic, force_generate=True)
        
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