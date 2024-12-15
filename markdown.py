# Using microsoft's library to convert docx into markdown for further processing with llms

from markitdown import MarkItDown
import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore",RuntimeWarning)
    markitdown = MarkItDown()
    result = markitdown.convert('generate-images.py')
    print(result)   