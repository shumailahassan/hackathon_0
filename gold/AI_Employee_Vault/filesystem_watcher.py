# filesystem_watcher.py
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import shutil
import time
import logging
from base_watcher import BaseWatcher

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

# Example usage
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Initialize and run the watcher
    vault_path = Path(__file__).parent  # Use the directory where the script is located
    watcher = FilesystemWatcher(str(vault_path))
    watcher.run()