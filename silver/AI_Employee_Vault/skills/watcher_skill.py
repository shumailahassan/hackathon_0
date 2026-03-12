"""
Watcher Skill - Contains all file system watching functionality
This skill supports file system monitoring for new files dropped in the Drop_Folder
"""
from pathlib import Path
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil
from abc import ABC, abstractmethod


class BaseWatcher(ABC):
    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def check_for_updates(self) -> list:
        '''Return list of new items to process'''
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        '''Create .md file in Needs_Action folder'''
        pass

    def run(self):
        self.logger.info(f'Starting {self.__class__.__name__}')
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    self.create_action_file(item)
            except Exception as e:
                self.logger.error(f'Error: {e}')
                # Log the error with error handling as required by Bronze Tier
                error_msg = f"Watcher error in {self.__class__.__name__}: {str(e)}"
                self.logger.error(error_msg)
                # Retry after a short delay
                time.sleep(5)
            time.sleep(self.check_interval)


class DropFolderHandler(FileSystemEventHandler):
    def __init__(self, vault_path: str):
        self.needs_action = Path(vault_path) / 'Needs_Action'
        self.logger = logging.getLogger(self.__class__.__name__)

    def on_created(self, event):
        if event.is_directory:
            return
        source = Path(event.src_path)
        if source.suffix.lower() in ['.txt', '.pdf', '.doc', '.docx', '.jpg', '.png', '.jpeg']:
            dest = self.needs_action / f'FILE_{source.name}'
            try:
                shutil.copy2(source, dest)
                self.create_metadata(source, dest)
                self.logger.info(f'New file {source.name} copied to Needs_Action folder')
            except Exception as e:
                self.logger.error(f'Error copying file {source.name}: {e}')
                # Retry mechanism
                try:
                    time.sleep(2)
                    shutil.copy2(source, dest)
                    self.create_metadata(source, dest)
                    self.logger.info(f'Retried - New file {source.name} copied to Needs_Action folder')
                except Exception as retry_error:
                    self.logger.error(f'Failed to copy file after retry: {retry_error}')


    def create_metadata(self, source: Path, dest: Path):
        meta_path = dest.with_suffix('.md')
        meta_content = f'''---
type: file_drop
original_name: {source.name}
size: {source.stat().st_size}
created: {time.strftime("%Y-%m-%d %H:%M:%S")}
---

New file dropped for processing from: {source}

This file has been detected and placed in the Needs_Action queue for the AI Employee to process.
'''
        meta_path.write_text(meta_content)


class FilesystemWatcher(BaseWatcher):
    def __init__(self, vault_path: str, watch_path: str = None):
        super().__init__(vault_path, check_interval=10)  # Check every 10 seconds
        self.watch_path = Path(watch_path) if watch_path else Path(vault_path) / 'Drop_Folder'
        # Create the watch folder if it doesn't exist
        self.watch_path.mkdir(exist_ok=True)
        self.handler = DropFolderHandler(vault_path)
        self.observer = Observer()
        self.observer.schedule(self.handler, str(self.watch_path), recursive=False)
        self.logger.info(f'Filesystem watcher initialized for: {self.watch_path}')

    def check_for_updates(self) -> list:
        # This is handled by the event handler, so we just ensure the observer is running
        if not self.observer.is_alive():
            self.observer.start()
        return []

    def create_action_file(self, item) -> Path:
        # This is handled by the event handler
        return Path("")

    def run(self):
        self.logger.info(f'Starting Filesystem Watcher for: {self.watch_path}')
        self.observer.start()
        try:
            while True:
                time.sleep(1)  # Keep the process alive
        except KeyboardInterrupt:
            self.logger.info('Stopping Filesystem Watcher...')
            self.observer.stop()
        self.observer.join()


def start_watcher(vault_path: str, watch_path: str = None):
    """
    Start the filesystem watcher to monitor for new files

    Args:
        vault_path (str): Path to the vault directory
        watch_path (str, optional): Path to watch for new files. Defaults to Drop_Folder in vault
    """
    watcher = FilesystemWatcher(vault_path, watch_path)
    return watcher


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Initialize and run the watcher
    vault_path = Path(__file__).parent  # Use the directory where the script is located
    watcher = start_watcher(str(vault_path))
    watcher.run()