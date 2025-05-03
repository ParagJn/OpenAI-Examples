# Jason-Viewer
import streamlit as st
import json

# Streamlit page configuration
st.set_page_config(
    page_title="JSON Viewer",
    layout="wide",            # Wide screen layout
    initial_sidebar_state="collapsed"  # Sidebar collapsed by default
)

# Title
st.title("📄 JSON Document Viewer")

# File uploader
uploaded_file = st.file_uploader("Upload a JSON document", type=["json"])

# Handle upload
if uploaded_file is not None:
    try:
        # Attempt to load the file as JSON
        json_data = json.load(uploaded_file)

        # Success message
        st.success("✅ JSON structure is valid!")

        # Extract keys for multiselect
        keys = list(json_data.keys())

        # Multiselect to choose keys to display
        selected_keys = st.multiselect("Choose JSON elements to display:", keys, default=keys)

        # Display nicely formatted JSON based on selected keys
        st.subheader("📘 Parsed JSON Content")
        filtered_json = {k: json_data[k] for k in selected_keys if k in json_data}
        st.json(filtered_json, expanded=True)

    except json.JSONDecodeError as e:
        # If JSON is invalid
        st.error(f"❌ Invalid JSON: {e}")
    except Exception as e:
        st.error(f"⚠️ An error occurred: {e}")
else:
    st.info("👆 Please upload a `.json` file to begin.")
