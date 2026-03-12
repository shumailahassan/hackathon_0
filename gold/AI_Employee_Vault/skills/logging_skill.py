"""
Logging Skill - Contains all functionality for logging actions in the AI Employee system
Keeps a simple log of all actions (what was read, written, moved)
"""
from pathlib import Path
import logging
import time
from datetime import datetime


def log_action(action: str, details: str = "", level: str = "INFO") -> bool:
    """
    Log an action with timestamp and details

    Args:
        action (str): The action being performed (e.g., 'read_file', 'move_file', 'write_content')
        details (str): Additional details about the action
        level (str): Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        bool: True if successful, False otherwise
    """
    logger = logging.getLogger(__name__)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {level}: {action} - {details}"

    try:
        if level == "DEBUG":
            logger.debug(log_message)
        elif level == "INFO":
            logger.info(log_message)
        elif level == "WARNING":
            logger.warning(log_message)
        elif level == "ERROR":
            logger.error(log_message)
        elif level == "CRITICAL":
            logger.critical(log_message)
        else:
            logger.info(log_message)  # Default to INFO

        return True
    except Exception as e:
        print(f"Error writing to log: {e}")
        return False


def log_file_read(file_path: str, content_preview: str = "") -> bool:
    """
    Log when a file is read from the vault

    Args:
        file_path (str): Path of the file being read
        content_preview (str): Preview of the content (optional)

    Returns:
        bool: True if successful, False otherwise
    """
    details = f"File: {file_path}"
    if content_preview:
        details += f", Preview: {content_preview[:100]}..."
    return log_action("read_file", details)


def log_file_write(file_path: str, content_size: int) -> bool:
    """
    Log when a file is written to the vault

    Args:
        file_path (str): Path of the file being written
        content_size (int): Size of content being written

    Returns:
        bool: True if successful, False otherwise
    """
    details = f"File: {file_path}, Size: {content_size} chars"
    return log_action("write_file", details)


def log_file_move(file_path: str, from_folder: str, to_folder: str) -> bool:
    """
    Log when a file is moved between folders

    Args:
        file_path (str): Path of the file being moved
        from_folder (str): Source folder
        to_folder (str): Destination folder

    Returns:
        bool: True if successful, False otherwise
    """
    details = f"File: {file_path}, From: {from_folder}, To: {to_folder}"
    return log_action("move_file", details)


def setup_logging_system(log_file_path: str = "ai_employee.log") -> None:
    """
    Set up the logging system with file and console handlers

    Args:
        log_file_path (str): Path to the log file
    """
    # Create a custom logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create handlers
    file_handler = logging.FileHandler(log_file_path)
    console_handler = logging.StreamHandler()

    # Create formatters and add it to handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def log_error(error_msg: str, context: str = "") -> bool:
    """
    Log an error with context

    Args:
        error_msg (str): The error message
        context (str): Context of where the error occurred

    Returns:
        bool: True if successful, False otherwise
    """
    details = f"Error: {error_msg}"
    if context:
        details += f", Context: {context}"
    return log_action("error", details, "ERROR")


def log_retry_attempt(action: str, error_msg: str, attempt: int, max_attempts: int) -> bool:
    """
    Log a retry attempt for a failed action

    Args:
        action (str): The action being retried
        error_msg (str): The error that caused the retry
        attempt (int): Current attempt number
        max_attempts (int): Maximum number of attempts

    Returns:
        bool: True if successful, False otherwise
    """
    details = f"Action: {action}, Error: {error_msg}, Attempt: {attempt}/{max_attempts}"
    return log_action("retry", details, "WARNING")


def log_system_status(status: str, details: str = "") -> bool:
    """
    Log system status changes

    Args:
        status (str): The status being logged
        details (str): Additional details about the status

    Returns:
        bool: True if successful, False otherwise
    """
    return log_action(f"system_{status}", details)


def get_recent_logs(log_file_path: str = "ai_employee.log", num_lines: int = 10) -> list:
    """
    Get recent log entries from the log file

    Args:
        log_file_path (str): Path to the log file
        num_lines (int): Number of recent lines to return

    Returns:
        list: List of recent log entries
    """
    try:
        with open(log_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return lines[-num_lines:] if len(lines) >= num_lines else lines
    except FileNotFoundError:
        return []
    except Exception as e:
        log_error(f"Error reading log file: {e}")
        return []


def initialize_logging_system():
    """
    Initialize the logging system for the AI Employee
    """
    log_file = "ai_employee.log"
    setup_logging_system(log_file)
    log_system_status("startup", "AI Employee logging system initialized")