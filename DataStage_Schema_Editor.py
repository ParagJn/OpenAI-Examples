import streamlit as st
import openai
import os
from tqdm import tqdm
from dotenv import load_dotenv
from datetime import datetime
import re
import pickle

st.set_page_config(page_title="DataStage Schema Editor", 
                   layout="wide", 
                   initial_sidebar_state="expanded"
                   )

class VectorDBManager:
    """
    Handles creation and management of vector stores.
    """

    class DataStageVectorStore:
        def __init__(self, name):
            self.id = "datastage_id_123"
            self.name = name
            self.created_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            class FileCounts:
                completed = 0
            self.file_counts = FileCounts()

    class DataStageClient:
        class vector_stores:
            @staticmethod
            def create(name):
                return VectorDBManager.DataStageVectorStore(name)

    def __init__(self, client=None):
        """
        Initialize with a vector DB client (e.g., OpenAI, Pinecone, etc.).
        If no client is provided, use the internal DataStageClient for demonstration.
        Args:
            client: The vector DB client instance.
        """
        if client is None:
            self.client = VectorDBManager.DataStageClient()
        else:
            self.client = client

    def create_vector_store(self, store_name: str) -> dict:
        """
        Create a new vector store with the given name.

        Args:
            store_name (str): Name for the vector store.

        Returns:
            dict: Details of the created vector store or empty dict on error.
        """
        try:
            vector_store = self.client.vector_stores.create(name=store_name)
            details = {
                "id": vector_store.id,
                "name": vector_store.name,
                "created_at": getattr(vector_store, "created_at", None),
                "file_count": getattr(getattr(vector_store, "file_counts", {}), "completed", None)
            }
            print("Vector store created:", details)
            return details
        except Exception as e:
            print(f"Error creating vector store: {e}")
            return {}

def extract_vector_records(content, max_record_length=4000):
    """
    Extract HEADER and DSJOB records from DataStage file content.
    For large records, splits them into nested DSSUBRECORD blocks to manage record size.
    Returns a list of records (strings).
    """
    patterns = [
        re.compile(r'(^BEGIN HEADER.*?^END HEADER)', re.DOTALL | re.MULTILINE),
        re.compile(r'(^BEGIN DSJOB.*?^END DSJOB)', re.DOTALL | re.MULTILINE)
    ]
    matches = []
    for pattern in patterns:
        matches.extend(list(pattern.finditer(content)))
    matches.sort(key=lambda m: m.start())
    
    records = []
    for m in matches:
        record = m.group(0).strip()
        # If record is too long, split into nested DSUBRECORDs
        if len(record) > max_record_length:
            lines = record.splitlines()
            header_line = lines[0]  # BEGIN HEADER or BEGIN DSJOB
            footer_line = lines[-1]  # END HEADER or END DSJOB
            body_lines = lines[1:-1]
            
            # Create DSUBRECORDs from the body
            subrecords = []
            current_chunk = []
            current_size = 0
            subrecord_count = 1
            
            for line in body_lines:
                line_size = len(line) + 1  # +1 for newline
                if current_size + line_size > max_record_length and current_chunk:
                    # Create a DSSUBRECORD from current chunk
                    subrecord = [f"BEGIN DSSUBRECORD {subrecord_count}"]
                    subrecord.extend(current_chunk)
                    subrecord.append(f"END DSSUBRECORD {subrecord_count}")
                    subrecords.append("\n".join(subrecord))
                    
                    # Reset for next chunk
                    current_chunk = []
                    current_size = 0
                    subrecord_count += 1
                
                current_chunk.append(line)
                current_size += line_size
            
            # Don't forget the last chunk
            if current_chunk:
                subrecord = [f"BEGIN DSSUBRECORD {subrecord_count}"]
                subrecord.extend(current_chunk)
                subrecord.append(f"END DSSUBRECORD {subrecord_count}")
                subrecords.append("\n".join(subrecord))
            
            # Reconstruct the full record with DSUBRECORDs
            nested_record = header_line + "\n" + "\n".join(subrecords) + "\n" + footer_line
            records.append(nested_record)
        else:
            # Record is not too long, keep as is
            records.append(record)
    
    return records

# Add a function to reassemble records from DSSUBRECORD blocks
def reassemble_dssubrecord(record):
    """
    Reassemble a full record by extracting and joining content from DSSUBRECORD blocks.
    Args:
        record (str): A record that may contain DSSUBRECORD blocks
    Returns:
        str: Reassembled record with DSSUBRECORD blocks merged
    """
    # Check if the record contains DSUBRECORDs
    if "BEGIN DSSUBRECORD" not in record:
        return record
    
    lines = record.splitlines()
    header_line = lines[0]
    footer_line = lines[-1]
    
    # Find all DSSUBRECORD blocks
    in_subrecord = False
    reassembled_lines = [header_line]
    
    for line in lines[1:-1]:
        if line.startswith("BEGIN DSSUBRECORD"):
            in_subrecord = True
            continue  # Skip the BEGIN DSSUBRECORD line
        elif line.startswith("END DSSUBRECORD"):
            in_subrecord = False
            continue  # Skip the END DSSUBRECORD line
        
        # Only include lines that are inside a DSSUBRECORD
        if in_subrecord:
            reassembled_lines.append(line)
    
    reassembled_lines.append(footer_line)
    return "\n".join(reassembled_lines)

def search_vector_record(records, query):
    """
    Search for all records containing the query string (case-insensitive).
    Returns a list of (index, record) tuples.
    """
    results = []
    for idx, rec in enumerate(records):
        if query.lower() in rec.lower():
            results.append((idx, rec))
    return results

# def update_vector_record_with_gpt(record, instruction, openai_api_key):
#     """
#     Use OpenAI GPT-4o to update the vector record as per instruction.
#     """
#     openai.api_key = openai_api_key
#     system_prompt = (
#         "You are a helpful assistant. The user will provide a DataStage export file record and a prompt describing changes to make. "
#         "You must make the requested changes, but you must strictly preserve the structure, format, and integrity of the DataStage record. "
#         "Do not break or corrupt the record. Only modify the relevant sections as per the user's request, and keep all other content unchanged. "
#         "Return the updated record as plain text."
#     )
#     messages = [
#         {"role": "system", "content": system_prompt},
#         {"role": "user", "content": f"Record:\n{record}"},
#         {"role": "user", "content": f"Change request: {instruction}"}
#     ]
#     response = openai.chat.completions.create(
#         model="gpt-4o",
#         messages=messages,
#         max_tokens=4096,
#         temperature=0.2,
#     )
#     return response.choices[0].message.content.strip()

def get_api_key():
    """
    Loads the OpenAI API key from .env file or returns None if not found.
    """
    load_dotenv()
    return os.getenv("OPENAI_API_KEY")

def get_vector_db_path(filename):
    """
    Returns the path to the vector db file for a given uploaded filename.
    """
    base_folder = "datastage_data"
    os.makedirs(base_folder, exist_ok=True)
    # Use only the filename, not the full path
    fname = os.path.basename(filename)
    return os.path.join(base_folder, f"{fname}.vectordb.pkl")

def save_vector_db(vector_records, filename):
    """
    Saves the vector records to a pickle file.
    """
    path = get_vector_db_path(filename)
    with open(path, "wb") as f:
        pickle.dump(vector_records, f)

def load_vector_db(filename):
    """
    Loads the vector records from a pickle file.
    Returns None if not found.
    """
    path = get_vector_db_path(filename)
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return None

def count_subrecords(record):
    """
    Count the number of DSSUBRECORD blocks within a record.
    
    Args:
        record (str): The record text to analyze
    
    Returns:
        int: The number of DSSUBRECORD blocks found
    """
    subrecord_pattern = re.compile(r'^BEGIN DSSUBRECORD \d+', re.MULTILINE)
    matches = subrecord_pattern.findall(record)
    return len(matches)

def main():
    st.sidebar.title("Settings")
    st.title("DataStage Schema File Editor")
    st.write("Upload a DataStage .dsx or .isx file, view vector records, and edit them using GPT-4o.")

    api_key = get_api_key()
    openai_api_key = api_key

    if not openai_api_key:
        openai_api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")
        if not openai_api_key:
            st.info("Please provide your OpenAI API Key in the .env file or enter it above to continue.")
            st.stop()

    # --- Performance optimization: Use session_state for vector db and file content ---
    if "vector_records" not in st.session_state:
        st.session_state.vector_records = None
    if "file_loaded" not in st.session_state:
        st.session_state.file_loaded = False
    if "vector_db_filename" not in st.session_state:
        st.session_state.vector_db_filename = None
    if "vector_db_loaded_from_disk" not in st.session_state:
        st.session_state.vector_db_loaded_from_disk = False

    uploaded_file = st.file_uploader("Upload your DataStage file (.dsx or .isx)", type=["dsx", "isx"])
    # If file is deleted (i.e., uploaded_file is None but file_loaded is True), reset everything
    if uploaded_file is None and st.session_state.get("file_loaded", False):
        st.session_state.vector_records = None
        st.session_state.file_loaded = False
        st.session_state.vector_db_filename = None
        st.session_state.vector_db_loaded_from_disk = False
        st.session_state.search_text = ""
        st.session_state.replace_text = ""
        st.session_state.show_results = False
        st.rerun()

    if uploaded_file and not st.session_state.file_loaded:
        filename = uploaded_file.name
        st.session_state.vector_db_filename = filename
        # Try to load from vector db
        vector_db = load_vector_db(filename)
        if vector_db is not None:
            st.session_state.vector_records = vector_db
            st.session_state.file_loaded = True
            st.session_state.vector_db_loaded_from_disk = True
            st.success(f"Loaded vector DB from local storage for file: {filename}")
        else:
            # Read file with progress bar
            file_size = uploaded_file.size
            content = ""
            with tqdm(total=file_size, unit='B', unit_scale=True, desc="Reading file") as pbar:
                while True:
                    chunk = uploaded_file.read(8192)
                    if not chunk:
                        break
                    content += chunk.decode("utf-8", errors="replace")
                    pbar.update(len(chunk))
            st.success(f"File loaded. Size: {len(content)} characters.")

            # Build vector store (extract records) and cache in session_state
            vector_records = extract_vector_records(content)
            st.session_state.vector_records = vector_records
            st.session_state.file_loaded = True
            st.session_state.vector_db_loaded_from_disk = False
            save_vector_db(vector_records, filename)
            st.success(f"Vector DB created and saved for file: {filename}")

    # If vector records are loaded, use them for display and editing
    if st.session_state.vector_records:
        records = st.session_state.vector_records
        st.info(f"Total vector records created: {len(records)}")

        # Ask user how many records to view
        num_records = st.sidebar.number_input("How many vector records do you want to view?", min_value=1, max_value=len(records), value=min(2, len(records)), step=1)
        # Sidebar: Option to delete and rebuild vector db if loaded from disk
        if st.session_state.get("vector_db_loaded_from_disk", False) and st.session_state.vector_db_filename:
            if st.sidebar.button("Delete & Rebuild Vector Data"):
                # Remove the vector db file and reset state to force rebuild
                vector_db_path = get_vector_db_path(st.session_state.vector_db_filename)
                if os.path.exists(vector_db_path):
                    os.remove(vector_db_path)
                st.session_state.vector_records = None
                st.session_state.file_loaded = False
                st.session_state.vector_db_loaded_from_disk = False
                st.rerun()

        
        cols = st.columns(2)
        for idx in range(num_records):
            col = cols[idx % 2]
            record_text = records[idx]
            col.text_area(f"Record # {idx+1}", value=record_text, height=500, key=f"record_{idx}")
            
            # Display number of subrecords below each text box
            subrecord_count = count_subrecords(record_text)
            if subrecord_count > 0:
                col.caption(f"Contains {subrecord_count} DSSUBRECORD blocks")
            else:
                col.caption("No DSSUBRECORD blocks (single record)")

        # Always show download button in sidebar
        if st.session_state.vector_records:
            updated_content = "\n\n".join(st.session_state.vector_records)
            st.sidebar.download_button(
                label="Download Updated DSX File",
                data=updated_content,
                file_name="updated_datastage.dsx",
                mime="text/plain"
            )

        # After any update to vector_records, save to disk
        def save_current_vector_db():
            if st.session_state.vector_db_filename:
                save_vector_db(st.session_state.vector_records, st.session_state.vector_db_filename)

        # Search and edit section
        st.markdown("---")
        # Use session state for search_query to allow clearing
        if "search_query" not in st.session_state:
            st.session_state.search_query = ""
        search_query = st.text_input("Enter a keyword to search for vector records to edit (case-insensitive):", value=st.session_state.search_query, key="main_search_query")
        found_results = []
        if search_query:
            found_results = search_vector_record(records, search_query)
            st.info(f"Found {len(found_results)} record(s) matching your search.")

        # Only show search/replace in sidebar if search results exist
        if found_results:
            # Use session state to persist search/replace values
            if "search_text" not in st.session_state:
                st.session_state.search_text = ""
            if "replace_text" not in st.session_state:
                st.session_state.replace_text = ""
            if "show_results" not in st.session_state:
                st.session_state.show_results = False

            col_btn1, col_btn2 = st.sidebar.columns([1,1])
            if col_btn1.button("View Search Results"):
                st.session_state.show_results = True
            if col_btn2.button("Clear Results"):
                st.session_state.show_results = False

            if st.session_state.show_results:
                result_cols = st.columns(2)
                for idx, (rec_idx, rec) in enumerate(found_results):
                    col = result_cols[idx % 2]
                    display_text = rec[:500] if len(rec) > 500 else rec
                    col.text_area(f"Search Result - Record # {rec_idx+1}", value=display_text, height=500, key=f"search_result_{rec_idx}")

                # Search and Replace in sidebar
                st.sidebar.markdown("---")
                search_text = st.sidebar.text_input("Search", value=st.session_state.search_text, key="search_text_input")
                replace_text = st.sidebar.text_input("Replace", value=st.session_state.replace_text, key="replace_text_input")
                st.session_state.search_text = search_text
                st.session_state.replace_text = replace_text

                if st.sidebar.button("Apply Search & Replace to Found Records"):
                    updated_count = 0
                    for rec_idx, rec in found_results:
                        if search_text:
                            new_rec = rec.replace(search_text, replace_text)
                            if new_rec != rec:
                                st.session_state.vector_records[rec_idx] = new_rec
                                updated_count += 1
                    save_current_vector_db()
                    st.sidebar.success(f"Updated {updated_count} record(s) with search & replace.")
                    # Clear the main search query after replace
                    st.session_state.search_query = ""
                    st.rerun()

        elif search_query:
            st.warning("No vector record found containing the given keyword.")

if __name__ == "__main__":
    main()
