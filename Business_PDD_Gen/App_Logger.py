#App-Logger.py
"""
App_Logger.py
This module provides a utility function to create and configure a logger instance
for logging application messages to a file.

Functions:
    get_logger(name="MyAppLogger", log_file="App.log", level=logging.INFO)
parag.jn@gmail.com
"""

import logging

# Create a logger function that can be imported and used in other modules
def get_logger(name="MyAppLogger", log_file="App.log", level=logging.INFO):
    """
    Returns a logger instance with the specified name and configuration.

    Args:
        name (str): The name of the logger.
        log_file (str): The file where logs will be written.
        level (int): The logging level (e.g., logging.INFO).

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)

    # Avoid adding multiple handlers
    if not logger.hasHandlers():
        logger.setLevel(level)

        # Create file handler
        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(
            "{asctime} - {levelname} - {message}",
            style="{",
            datefmt="%Y-%m-%d %H:%M",
        ))

        # Add the file handler to the logger
        logger.addHandler(file_handler)

    return logger