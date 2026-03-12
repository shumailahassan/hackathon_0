# orchestrator.py
import os
import sys
import time
import logging
from pathlib import Path
from filesystem_watcher import FilesystemWatcher
import threading

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


def check_pending_approval(vault_path: str):
    """Check if there are any files in the Pending_Approval folder"""
    pending_path = Path(vault_path) / 'Pending_Approval'
    if pending_path.exists():
        files = list(pending_path.glob('*'))
        if files:
            logger.info(f'Found {len(files)} files pending approval')
            for file in files:
                logger.info(f'  - {file.name}')
            return files
    return []


def process_approval_file(vault_path: str, file_path: Path):
    """Process an approved file and take action"""
    logger.info(f'Processing approval file: {file_path.name}')

    try:
        # Read the approval file to get action details
        content = file_path.read_text()

        # In a real implementation, this would trigger the actual action
        # For now, we'll just move it to Done as if it was processed
        done_path = Path(vault_path) / 'Done'
        new_file_path = done_path / file_path.name
        file_path.rename(new_file_path)
        logger.info(f'Moved {file_path.name} to Done folder after approval processing')
    except Exception as e:
        logger.error(f'Error processing approval file {file_path.name}: {e}')


def run_reasoning_loop(vault_path: str):
    """Run the reasoning loop in a separate thread"""
    try:
        from reasoning_loop import ReasoningLoop
        reasoning_loop = ReasoningLoop(vault_path)
        reasoning_loop.run()
    except ImportError as e:
        logger.error(f"Failed to import reasoning_loop: {e}")
        logger.info("Please ensure reasoning_loop.py is in the vault directory")
    except Exception as e:
        logger.error(f"Error running reasoning loop: {e}")

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

    # Move the file to Done folder after processing
    done_path = Path(vault_path) / 'Done'
    new_file_path = done_path / file_path.name
    file_path.rename(new_file_path)
    logger.info(f'Moved {file_path.name} to Done folder')

def main():
    logger.info("Starting AI Employee Orchestrator...")

    # Get vault path from command line argument or use current directory
    vault_path = sys.argv[1] if len(sys.argv) > 1 else "."
    logger.info(f"Using vault path: {vault_path}")

    # Create the Drop_Folder if it doesn't exist
    drop_folder = Path(vault_path) / 'Drop_Folder'
    drop_folder.mkdir(exist_ok=True)
    logger.info(f"Drop folder created at: {drop_folder}")

    # Start all watchers in separate threads
    import threading

    # Start the filesystem watcher
    fs_watcher = FilesystemWatcher(vault_path, str(drop_folder))
    def run_fs_watcher():
        fs_watcher.run()

    fs_thread = threading.Thread(target=run_fs_watcher, daemon=True)
    fs_thread.start()

    # Try to start Gmail watcher (optional - requires credentials)
    try:
        from gmail_watcher import GmailWatcher
        gmail_watcher = GmailWatcher(vault_path)
        def run_gmail_watcher():
            try:
                gmail_watcher.run()
            except Exception as e:
                logger.warning(f"Gmail watcher failed to start (this is OK if credentials not set up): {e}")

        gmail_thread = threading.Thread(target=run_gmail_watcher, daemon=True)
        gmail_thread.start()
        logger.info("Gmail watcher started.")
    except ImportError as e:
        logger.warning(f"Gmail watcher not available: {e}")
    except Exception as e:
        logger.warning(f"Gmail watcher failed to start: {e}")

    # Try to start WhatsApp watcher (optional)
    try:
        from whatsapp_watcher import WhatsAppWatcher
        whatsapp_watcher = WhatsAppWatcher(vault_path)
        def run_whatsapp_watcher():
            try:
                whatsapp_watcher.run()
            except Exception as e:
                logger.warning(f"WhatsApp watcher requires Playwright setup: {e}")

        whatsapp_thread = threading.Thread(target=run_whatsapp_watcher, daemon=True)
        whatsapp_thread.start()
        logger.info("WhatsApp watcher started.")
    except ImportError as e:
        logger.warning(f"WhatsApp watcher not available: {e}")
    except Exception as e:
        logger.warning(f"WhatsApp watcher failed to start: {e}")

    # Try to start LinkedIn watcher (optional)
    try:
        from linkedin_watcher import LinkedInWatcher
        linkedin_watcher = LinkedInWatcher(vault_path)
        def run_linkedin_watcher():
            try:
                linkedin_watcher.run()
            except Exception as e:
                logger.warning(f"LinkedIn watcher requires Playwright setup: {e}")

        linkedin_thread = threading.Thread(target=run_linkedin_watcher, daemon=True)
        linkedin_thread.start()
        logger.info("LinkedIn watcher started.")
    except ImportError as e:
        logger.warning(f"LinkedIn watcher not available: {e}")
    except Exception as e:
        logger.warning(f"LinkedIn watcher failed to start: {e}")

    # Start the reasoning loop in a separate thread
    reasoning_thread = threading.Thread(target=run_reasoning_loop, args=(vault_path,), daemon=True)
    reasoning_thread.start()
    logger.info("Reasoning loop started.")

    logger.info("All components started.")
    logger.info(f"You can drop files into: {drop_folder}")
    logger.info("The AI Employee will detect new files and process them.")
    logger.info("Ctrl+C to stop the orchestrator.")

    try:
        while True:
            # Check for files that need action
            needs_action_files = check_needs_action(vault_path)
            for file_path in needs_action_files:
                # In Silver tier, these will be processed by the reasoning loop
                logger.info(f"New file in Needs_Action: {file_path.name}")

            # Check for files that need approval processing
            pending_approval_files = check_pending_approval(vault_path)
            for file_path in pending_approval_files:
                # Check if the file has been moved to Approved folder
                approved_path = Path(vault_path) / 'Approved'
                approved_file = approved_path / file_path.name
                if approved_file.exists():
                    process_approval_file(vault_path, approved_file)

            time.sleep(5)  # Check every 5 seconds

    except KeyboardInterrupt:
        logger.info("Orchestrator stopped by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()