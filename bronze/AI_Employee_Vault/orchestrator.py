# orchestrator.py
import os
import sys
import time
import logging
from pathlib import Path
# Import the watcher skill
from skills.watcher_skill import FilesystemWatcher, start_watcher
# Import the vault read skill
from skills.vault_read_skill import check_needs_action
# Import the vault write skill
from skills.vault_write_skill import move_file_to_done, update_dashboard_status

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('orchestrator.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def check_needs_action(vault_path: str):
    """Check if there are any files in the Needs_Action folder"""
    needs_action_path = Path(vault_path) / 'Needs_Action'
    if needs_action_path.exists():
        files = list(needs_action_path.glob('*'))
        if files:
            logger.info(f'Found {len(files)} files in Needs_Action folder')
            for file in files:
                logger.info(f'  - {file.name}')
            return files
    return []

def process_needs_action_file(vault_path: str, file_path: Path):
    """Process a single file from Needs_Action folder"""
    logger.info(f'Processing file: {file_path.name}')

    # For Bronze tier, we'll just print a message
    # In higher tiers, Claude would process these files
    print(f"\n*** NEW TASK DETECTED ***")
    print(f"File: {file_path.name}")
    print(f"Path: {file_path}")
    print(f"Content preview:")
    content = file_path.read_text()
    print(content[:500] + "..." if len(content) > 500 else content)
    print("*** END TASK ***\n")

    # Move the file to Done folder after processing using the vault write skill
    success = move_file_to_done(vault_path, file_path)
    if success:
        logger.info(f'Moved {file_path.name} to Done folder')
    else:
        logger.error(f'Failed to move {file_path.name} to Done folder')

def main():
    logger.info("Starting AI Employee Orchestrator...")

    # Get vault path from command line argument or use current directory
    vault_path = sys.argv[1] if len(sys.argv) > 1 else "."
    logger.info(f"Using vault path: {vault_path}")

    # Create the Drop_Folder if it doesn't exist
    drop_folder = Path(vault_path) / 'Drop_Folder'
    drop_folder.mkdir(exist_ok=True)
    logger.info(f"Drop folder created at: {drop_folder}")

    # Start the filesystem watcher in a separate thread using the skill
    import threading
    watcher = start_watcher(vault_path, str(drop_folder))

    def run_watcher():
        watcher.run()

    watcher_thread = threading.Thread(target=run_watcher, daemon=True)
    watcher_thread.start()

    logger.info("Filesystem watcher started.")
    logger.info(f"You can now drop files into: {drop_folder}")
    logger.info("The AI Employee will detect new files and place them in Needs_Action folder.")
    logger.info("Ctrl+C to stop the orchestrator.")

    try:
        while True:
            # Check for files that need action using the skill
            needs_action_files = check_needs_action(vault_path)

            for file_path in needs_action_files:
                process_needs_action_file(vault_path, file_path)

            # Update dashboard status with current counts
            needs_action_count = len(check_needs_action(vault_path))
            update_dashboard_status(vault_path, status="Running", active_tasks=0, pending_actions=needs_action_count)

            time.sleep(5)  # Check every 5 seconds

    except KeyboardInterrupt:
        logger.info("Orchestrator stopped by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()