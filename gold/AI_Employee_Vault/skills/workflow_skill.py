"""
Workflow Skill - Contains all functionality for moving items between folders in the AI Employee workflow
(/Inbox → /Needs_Action → /Done)
"""
from pathlib import Path
import logging
import time
import shutil


def move_file_to_needs_action(vault_path: str, file_path: Path) -> bool:
    """
    Move a file from Inbox to Needs_Action folder

    Args:
        vault_path (str): Path to the vault directory
        file_path (Path): Path to the file to move

    Returns:
        bool: True if successful, False otherwise
    """
    logger = logging.getLogger(__name__)
    needs_action_path = Path(vault_path) / 'Needs_Action'
    new_file_path = needs_action_path / file_path.name

    try:
        # Create Needs_Action directory if it doesn't exist
        needs_action_path.mkdir(exist_ok=True)

        # Rename/move the file
        file_path.rename(new_file_path)
        logger.info(f'Moved {file_path.name} to Needs_Action folder')
        return True
    except Exception as e:
        logger.error(f'Error moving {file_path.name} to Needs_Action folder: {e}')
        # Try again after a short delay
        try:
            time.sleep(2)
            file_path.rename(new_file_path)
            logger.info(f'Retried - Moved {file_path.name} to Needs_Action folder')
            return True
        except Exception as retry_error:
            logger.error(f'Failed to move file after retry: {retry_error}')
            return False


def move_file_to_done(vault_path: str, file_path: Path) -> bool:
    """
    Move a file from Needs_Action to Done folder

    Args:
        vault_path (str): Path to the vault directory
        file_path (Path): Path to the file to move

    Returns:
        bool: True if successful, False otherwise
    """
    logger = logging.getLogger(__name__)
    done_path = Path(vault_path) / 'Done'
    new_file_path = done_path / file_path.name

    try:
        # Create Done directory if it doesn't exist
        done_path.mkdir(exist_ok=True)

        # Rename/move the file
        file_path.rename(new_file_path)
        logger.info(f'Moved {file_path.name} to Done folder')
        return True
    except Exception as e:
        logger.error(f'Error moving {file_path.name} to Done folder: {e}')
        # Try again after a short delay
        try:
            time.sleep(2)
            file_path.rename(new_file_path)
            logger.info(f'Retried - Moved {file_path.name} to Done folder')
            return True
        except Exception as retry_error:
            logger.error(f'Failed to move file after retry: {retry_error}')
            return False


def move_file_to_inbox(vault_path: str, file_path: Path) -> bool:
    """
    Move a file to Inbox folder

    Args:
        vault_path (str): Path to the vault directory
        file_path (Path): Path to the file to move

    Returns:
        bool: True if successful, False otherwise
    """
    logger = logging.getLogger(__name__)
    inbox_path = Path(vault_path) / 'Inbox'
    new_file_path = inbox_path / file_path.name

    try:
        # Create Inbox directory if it doesn't exist
        inbox_path.mkdir(exist_ok=True)

        # Rename/move the file
        file_path.rename(new_file_path)
        logger.info(f'Moved {file_path.name} to Inbox folder')
        return True
    except Exception as e:
        logger.error(f'Error moving {file_path.name} to Inbox folder: {e}')
        # Try again after a short delay
        try:
            time.sleep(2)
            file_path.rename(new_file_path)
            logger.info(f'Retried - Moved {file_path.name} to Inbox folder')
            return True
        except Exception as retry_error:
            logger.error(f'Failed to move file after retry: {retry_error}')
            return False


def get_next_action_files(vault_path: str) -> list:
    """
    Get all files from the Needs_Action folder that need processing

    Args:
        vault_path (str): Path to the vault directory

    Returns:
        list: List of file paths in the Needs_Action folder
    """
    logger = logging.getLogger(__name__)
    needs_action_path = Path(vault_path) / 'Needs_Action'

    if not needs_action_path.exists():
        logger.warning(f"Needs_Action folder does not exist: {needs_action_path}")
        return []

    try:
        files = list(needs_action_path.glob('*'))
        logger.info(f"Found {len(files)} files in Needs_Action folder")
        return files
    except Exception as e:
        logger.error(f"Error listing files in Needs_Action folder: {e}")
        return []


def get_processed_files(vault_path: str) -> list:
    """
    Get all files from the Done folder

    Args:
        vault_path (str): Path to the vault directory

    Returns:
        list: List of file paths in the Done folder
    """
    logger = logging.getLogger(__name__)
    done_path = Path(vault_path) / 'Done'

    if not done_path.exists():
        logger.warning(f"Done folder does not exist: {done_path}")
        return []

    try:
        files = list(done_path.glob('*'))
        logger.info(f"Found {len(files)} files in Done folder")
        return files
    except Exception as e:
        logger.error(f"Error listing files in Done folder: {e}")
        return []


def get_inbox_files(vault_path: str) -> list:
    """
    Get all files from the Inbox folder

    Args:
        vault_path (str): Path to the vault directory

    Returns:
        list: List of file paths in the Inbox folder
    """
    logger = logging.getLogger(__name__)
    inbox_path = Path(vault_path) / 'Inbox'

    if not inbox_path.exists():
        logger.warning(f"Inbox folder does not exist: {inbox_path}")
        return []

    try:
        files = list(inbox_path.glob('*'))
        logger.info(f"Found {len(files)} files in Inbox folder")
        return files
    except Exception as e:
        logger.error(f"Error listing files in Inbox folder: {e}")
        return []


def process_workflow_step(vault_path: str, file_path: Path, from_folder: str, to_folder: str) -> bool:
    """
    Generic function to move a file from one specific folder to another

    Args:
        vault_path (str): Path to the vault directory
        file_path (Path): Path to the file to move
        from_folder (str): Source folder name (e.g., 'Inbox', 'Needs_Action')
        to_folder (str): Destination folder name (e.g., 'Needs_Action', 'Done')

    Returns:
        bool: True if successful, False otherwise
    """
    logger = logging.getLogger(__name__)

    # Validate folder names
    valid_folders = ['Inbox', 'Needs_Action', 'Done']
    if from_folder not in valid_folders or to_folder not in valid_folders:
        logger.error(f"Invalid folder names: {from_folder} -> {to_folder}")
        return False

    # Get the source and destination paths
    from_path = Path(vault_path) / from_folder
    to_path = Path(vault_path) / to_folder
    expected_file_path = from_path / file_path.name

    # Verify the file exists in the source folder
    if not expected_file_path.exists():
        logger.error(f"File {file_path.name} does not exist in {from_folder} folder")
        return False

    # Create destination directory if it doesn't exist
    to_path.mkdir(exist_ok=True)

    # Create destination file path
    dest_file_path = to_path / file_path.name

    # Try to move the file
    try:
        expected_file_path.rename(dest_file_path)
        logger.info(f'Moved {file_path.name} from {from_folder} to {to_folder} folder')
        return True
    except Exception as e:
        logger.error(f'Error moving {file_path.name} from {from_folder} to {to_folder}: {e}')
        # Try again after a short delay
        try:
            time.sleep(2)
            expected_file_path.rename(dest_file_path)
            logger.info(f'Retried - Moved {file_path.name} from {from_folder} to {to_folder} folder')
            return True
        except Exception as retry_error:
            logger.error(f'Failed to move file after retry: {retry_error}')
            return False