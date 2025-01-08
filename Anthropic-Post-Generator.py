import streamlit as st
from anthropic import Anthropic
from dotenv import load_dotenv
import json
import os
from datetime import datetime
from functools import lru_cache

# Initialize Anthropic client
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
anthropic = Anthropic(api_key=api_key)

# Constants
JSON_FILE = 'social_media_posts.json'
CACHE_FILE = 'cache.json'
BATCH_SIZE = 10  # Number of posts to keep in memory

# Initialize session state
if 'cache' not in st.session_state:
    st.session_state.cache = {}
if 'posts' not in st.session_state:
    st.session_state.posts = []

@lru_cache(maxsize=100)
def load_cache():
    """Cache loader with LRU cache decorator"""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def ensure_file_exists(filename):
    """Ensure JSON file exists and is properly initialized"""
    try:
        if not os.path.exists(filename):
            with open(filename, 'w') as f:
                json.dump([], f)
            st.toast(f"Created new file: {filename}")
        return True
    except Exception as e:
        st.error(f"Error creating file {filename}: {str(e)}")
        return False

def batch_save_to_json(data):
    """Batch process JSON saves with proper file handling"""
    try:
        ensure_file_exists(JSON_FILE)
        
        # Load existing data
        try:
            with open(JSON_FILE, 'r') as f:
                existing_data = json.load(f)
        except json.JSONDecodeError:
            existing_data = []
        
        # Append new data
        existing_data.append(data)
        
        # Write back to file
        with open(JSON_FILE, 'w') as f:
            json.dump(existing_data, f, indent=4)
        
        st.toast(f"Successfully saved to {JSON_FILE}")
        return True
    except Exception as e:
        st.error(f"Error saving to JSON: {str(e)}")
        return False

def generate_content(platform, topic, force_generate=False):
    """Optimized content generation"""
    cache_key = f"{platform}_{topic}"
    
    # Check session state cache first
    if not force_generate and cache_key in st.session_state.cache:
        return st.session_state.cache[cache_key]

    try:
        char_limits = {"Twitter": 280, "Instagram": 2200, "Facebook": 63206}
        prompt = f"""You are tasked with generating a social media post for {platform} about {topic}.
Character limit: {char_limits[platform]}
Output format: <post>Your post here</post>"""

        # Streamlined API call
        message = anthropic.messages.create(
            model="claude-3-5-sonnet-20240620",
            system="Expert social media post generator",
            max_tokens=300,  # Reduced tokens for faster response
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = message.content[0].text
        
        # Update session state cache
        st.session_state.cache[cache_key] = content
        
        # Async cache save
        if len(st.session_state.cache) > 100:
            # Implement cache cleanup for oldest entries
            st.session_state.cache = dict(list(st.session_state.cache.items())[-100:])
        
        return content
    except Exception as e:
        st.error(f"Generation error: {str(e)}")
        return None

# Streamlit UI with optimizations
st.title("Social Media Post Generator")

col1, col2 = st.columns(2)
with col1:
    platform = st.selectbox("Platform", ["Twitter", "Instagram", "Facebook"])
with col2:
    topic = st.text_input("Topic")

char_limits = {"Twitter": 280, "Instagram": 2200, "Facebook": 63206}
st.write(f"Character limit: {char_limits[platform]}")

if st.button("Generate"):
    if topic and len(topic) <= char_limits[platform]:
        with st.spinner("Generating..."):
            content = generate_content(platform, topic, force_generate=True)
            if content:
                st.write("Generated Post:", content)
                batch_save_to_json({
                    "platform": platform,
                    "topic": topic,
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                })
    else:
        st.warning("Invalid topic length")

# Efficient post display with proper error handling
st.write("---")
st.subheader("Previously Generated Posts")

if ensure_file_exists(JSON_FILE):
    try:
        with open(JSON_FILE, 'r') as f:
            try:
                posts = json.load(f)
                if posts:
                    # Display last 10 posts
                    for post in list(reversed(posts))[:10]:
                        st.write(f"Platform: {post['platform']}")
                        st.write(f"Topic: {post['topic']}")
                        st.write(f"Content: {post['content']}")
                        st.write(f"Timestamp: {post['timestamp']}")
                        st.write("---")
                else:
                    st.info("No posts available yet.")
            except json.JSONDecodeError:
                st.error("Error reading posts: Invalid JSON format")
    except Exception as e:
        st.error(f"Error reading posts file: {str(e)}")
else:
    st.error("Could not access posts file")