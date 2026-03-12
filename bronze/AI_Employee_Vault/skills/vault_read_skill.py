"""
Vault Read Skill - Contains all functionality for reading from the Obsidian vault
"""
from pathlib import Path
import logging


def read_from_vault(path: str) -> str:
    """
    Read content from a file in the vault

    Args:
        path (str): Path to the file to read

    Returns:
        str: Content of the file, or empty string if file doesn't exist
    """
    logger = logging.getLogger(__name__)
    file_path = Path(path)

    if not file_path.exists():
        logger.warning(f"File does not exist: {file_path}")
        return ""

    try:
        content = file_path.read_text(encoding='utf-8')
        logger.info(f"Successfully read file: {file_path}")
        return content
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return ""


def read_dashboard_content(vault_path: str) -> str:
    """
    Read the dashboard file from the vault

    Args:
        vault_path (str): Path to the vault directory

    Returns:
        str: Content of Dashboard.md
    """
    dashboard_path = Path(vault_path) / "Dashboard.md"
    return read_from_vault(str(dashboard_path))


def read_company_handbook(vault_path: str) -> str:
    """
    Read the company handbook from the vault

    Args:
        vault_path (str): Path to the vault directory

    Returns:
        str: Content of Company_Handbook.md
    """
    handbook_path = Path(vault_path) / "Company_Handbook.md"
    return read_from_vault(str(handbook_path))


def list_files_in_folder(vault_path: str, folder_name: str) -> list:
    """
    List all files in a specific folder within the vault

    Args:
        vault_path (str): Path to the vault directory
        folder_name (str): Name of the folder to list files from

    Returns:
        list: List of file paths in the folder
    """
    logger = logging.getLogger(__name__)
    folder_path = Path(vault_path) / folder_name

    if not folder_path.exists():
        logger.warning(f"Folder does not exist: {folder_path}")
        return []

    try:
        files = list(folder_path.glob('*'))
        logger.info(f"Found {len(files)} files in {folder_path}")
        return files
    except Exception as e:
        logger.error(f"Error listing files in {folder_path}: {e}")
        return []


def get_needs_action_files(vault_path: str) -> list:
    """
    Get all files from the Needs_Action folder

    Args:
        vault_path (str): Path to the vault directory

    Returns:
        list: List of file paths in the Needs_Action folder
    """
    return list_files_in_folder(vault_path, 'Needs_Action')


def check_needs_action(vault_path: str):
    """Check if there are any files in the Needs_Action folder"""
    needs_action_path = Path(vault_path) / 'Needs_Action'
    if needs_action_path.exists():
        files = list(needs_action_path.glob('*'))
        if files:
            return files
    return []