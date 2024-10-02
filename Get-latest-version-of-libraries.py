"""
Library Version Checker and Progress Bar Script

Description:
------------
This Python script processes a list of libraries with their current versions,
checks if there are newer versions available using `pip index versions`, and
writes the results to a `requirements.txt` file. For each library:
- If a newer version is available, the latest version is recorded.
- If the library is already up to date or an error occurs, the current version
  is written to the file as is.

Additionally, the script provides a visual progress bar in the format:
[ == % done == ] to indicate the progress of library version checking.

Key Features:
-------------
- Check for the latest versions of Python libraries.
- Generate or update `requirements.txt` with current/latest versions.
- Display a dynamic Linux-style progress bar to track the processing of libraries.

Functions:
----------
- progress_bar(): Displays a dynamic progress bar.
- process_libraries(): Processes each library, checks for new versions, and writes results.

"""

import subprocess
import time

old_libraries = [
    "click==8.1.7",
    "docx==0.2.4",
    "docx2pdf==0.1.8",
    "docx2txt==0.8",
    "fastapi==0.111.0",
    "genai==2.1.0",
    "langchain==0.1.17",
    "pdf2image==1.17.0",
    "pandas==2.2.2",
    "pillow==10.2.0",
    "pydantic==2.7.2",
    "python-dotenv==1.0.1",
    "python_docx==1.1.0",
    "PyYAML==6.0.1",
    "requests==2.32.3",
    "starlette==0.37.2",
    "text_generation==0.6.1",
    "transformers==4.36.0",
    "uvicorn==0.28.0",
    "streamlit==1.32.2",
    "openpyxl==3.1.2",
    "jwt==1.3.1",
    "PyJWT==2.8.0",
    "opencv-python-headless==4.10.0.84",
    "contrast-agent==9.1.0"
]

# simple progress bar
def progress_bar(progress, total, bar_length=40):
    percent = int((progress / total) * 100)
    bar_filled = int((progress / total) * bar_length)
    bar = '=' * bar_filled + ' ' * (bar_length - bar_filled)
    print(f"\r[ {bar} {percent}% libraries processed ]", end='')

# generate the new requirements.txt file
def process_libraries():
    total_libraries = len(old_libraries)
    with open("requirements.txt", "w") as f:
        for idx, library in enumerate(old_libraries):
            library_name, current_version = library.split("==")
            try:
                # Get the latest version of the library using 'pip index versions'
                latest_version_output = subprocess.check_output(
                    ["pip", "index", "versions", library_name],
                    stderr=subprocess.STDOUT
                ).decode()
                
                # Extract the latest version from the output
                latest_version = current_version  # Default to the current version
                lines = latest_version_output.splitlines()
                for line in lines:
                    if line.strip().startswith("LATEST:"):
                        latest_version = line.split()[1]  # Extract version after "LATEST:"
                        break
                
                # Write either the latest version or the current version if already up to date
                f.write(f"{library_name}=={latest_version}\n")
            
            except (subprocess.CalledProcessError, IndexError):
                # If there's an error (e.g., package not found), write the original version to the file
                f.write(library + "\n")
            
            # Update the progress bar after each library is processed
            progress_bar(idx + 1, total_libraries)
            time.sleep(0.1)  # Simulate processing time for better visual effect

print("Processing libraries...\n")
process_libraries()
print("\nDone! Check requirements.txt file to get latest version of the libraries")
