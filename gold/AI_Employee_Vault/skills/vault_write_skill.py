"""
Vault Write Skill - Contains all functionality for writing to the Obsidian vault
"""
from pathlib import Path
import logging
import time
import shutil
import re


def write_to_vault(path: str, content: str) -> bool:
    """
    Write content to a file in the vault

    Args:
        path (str): Path to the file to write
        content (str): Content to write to the file

    Returns:
        bool: True if successful, False otherwise
    """
    logger = logging.getLogger(__name__)
    file_path = Path(path)

    try:
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        file_path.write_text(content, encoding='utf-8')
        logger.info(f"Successfully wrote to file: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error writing to file {file_path}: {e}")
        return False


def update_dashboard_field(vault_path: str, field: str, new_value: str) -> bool:
    """
    Update a specific field in the Dashboard.md file

    Args:
        vault_path (str): Path to the vault directory
        field (str): Field name to update (e.g., 'Active Tasks', 'Pending Actions')
        new_value (str): New value for the field

    Returns:
        bool: True if successful, False otherwise
    """
    dashboard_path = Path(vault_path) / "Dashboard.md"

    try:
        content = dashboard_path.read_text(encoding='utf-8')
    except FileNotFoundError:
        logging.getLogger(__name__).warning(f"Dashboard.md does not exist: {dashboard_path}")
        return False

    # Replace the specific field in the content
    if field == 'Active Tasks':
        pattern = r'(- \*\*Active Tasks\*\*: )(.+)'
        replacement = rf'\g<1>{new_value}'
    elif field == 'Pending Actions':
        pattern = r'(- \*\*Pending Actions\*\*: )(.+)'
        replacement = rf'\g<1>{new_value}'
    elif field == 'Current Status':
        pattern = r'(- \*\*AI Employee Status\*\*: )(.+)'
        replacement = rf'\g<1>{new_value}'
    else:
        # Generic field update - looks for patterns like "- **FieldName**: value"
        pattern = rf'(- \*\*{field}\*\*: )(.+)'
        replacement = rf'\g<1>{new_value}'

    updated_content = re.sub(pattern, replacement, content)

    if updated_content != content:
        return write_to_vault(str(dashboard_path), updated_content)
    else:
        # Field not found, append it to the Current Status section
        updated_content = content.replace(
            '- **AI Employee Status**: Running',
            f'- **AI Employee Status**: Running\n- **{field}**: {new_value}'
        )
        return write_to_vault(str(dashboard_path), updated_content)


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
        return False


def create_task_file(vault_path: str, task_name: str, content: str) -> bool:
    """
    Create a task file in the Needs_Action folder

    Args:
        vault_path (str): Path to the vault directory
        task_name (str): Name of the task file
        content (str): Content for the task file

    Returns:
        bool: True if successful, False otherwise
    """
    needs_action_path = Path(vault_path) / 'Needs_Action'
    task_file_path = needs_action_path / f"{task_name}.md"

    # Create Needs_Action directory if it doesn't exist
    needs_action_path.mkdir(exist_ok=True)

    return write_to_vault(str(task_file_path), content)


def update_dashboard_status(vault_path: str, status: str = "Running", active_tasks: int = 0, pending_actions: int = 0):
    """
    Update the main status fields in the Dashboard.md file
    """
    dashboard_path = Path(vault_path) / "Dashboard.md"

    try:
        content = dashboard_path.read_text(encoding='utf-8')
    except FileNotFoundError:
        logging.getLogger(__name__).warning(f"Dashboard.md does not exist: {dashboard_path}")
        # Create a basic dashboard if it doesn't exist
        content = f"""# AI Employee Dashboard

## Overview
This dashboard provides a real-time summary of your personal and business activities managed by your AI Employee.

## Current Status
- **Last Update**: {time.strftime("%Y-%m-%d %H:%M:%S")}
- **AI Employee Status**: {status}
- **Active Tasks**: {active_tasks}
- **Pending Actions**: {pending_actions}

## Recent Activity
- [No recent activity]

## Alerts & Notifications
- [No alerts]

## Next Actions
- [No pending actions]

## Business Metrics
- **Current Month Revenue**: $0.00
- **Active Projects**: 0
- **Pending Invoices**: 0

## System Status
- **Watchers Active**: 0
- **Last Watcher Check**: Never
- **Vault Sync Status**: Local only
"""

    # Update status fields using regex
    content = re.sub(r'(- \*\*AI Employee Status\*\*: ).+', rf'\g<1>{status}', content)
    content = re.sub(r'(- \*\*Active Tasks\*\*: )\d+', rf'\g<1>{active_tasks}', content)
    content = re.sub(r'(- \*\*Pending Actions\*\*: )\d+', rf'\g<1>{pending_actions}', content)

    # Update the last update timestamp
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    content = re.sub(r'(- \*\*Last Update\*\*: ).+', rf'\g<1>{current_time}', content)

    # Write back to file
    return write_to_vault(str(dashboard_path), content)


def log_activity(vault_path: str, activity: str):
    """
    Log an activity to the Dashboard.md file
    """
    dashboard_path = Path(vault_path) / "Dashboard.md"

    try:
        content = dashboard_path.read_text(encoding='utf-8')
    except FileNotFoundError:
        logging.getLogger(__name__).warning(f"Dashboard.md does not exist: {dashboard_path}")
        # Create a basic dashboard if it doesn't exist
        content = f"""# AI Employee Dashboard

## Overview
This dashboard provides a real-time summary of your personal and business activities managed by your AI Employee.

## Current Status
- **Last Update**: {time.strftime("%Y-%m-%d %H:%M:%S")}
- **AI Employee Status**: Running
- **Active Tasks**: 0
- **Pending Actions**: 0

## Recent Activity
- {activity}

## Alerts & Notifications
- [No alerts]

## Next Actions
- [No pending actions]

## Business Metrics
- **Current Month Revenue**: $0.00
- **Active Projects**: 0
- **Pending Invoices**: 0

## System Status
- **Watchers Active**: 0
- **Last Watcher Check**: Never
- **Vault Sync Status**: Local only
"""

    # Find the Recent Activity section and add the new activity
    lines = content.split('\n')
    new_lines = []
    activity_added = False

    for line in lines:
        new_lines.append(line)
        if line.strip() == '## Recent Activity' and not activity_added:
            # Check if there's already a "[No recent activity]" placeholder
            if len(new_lines) < len(lines) and '[No recent activity]' in lines[lines.index(line) + 1]:
                # Replace the placeholder
                new_lines[-1] = f'- {activity}'  # Replace the [No recent activity] line
            else:
                new_lines.append(f'- {activity}')
            activity_added = True

    # Replace [No recent activity] if it exists elsewhere
    content = '\n'.join(new_lines)
    content = content.replace('- [No recent activity]\n', '')  # Remove placeholder

    # Write back to file
    return write_to_vault(str(dashboard_path), content)