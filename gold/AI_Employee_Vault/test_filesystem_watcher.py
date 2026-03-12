# test_filesystem_watcher.py
import os
import time
from pathlib import Path

def test_filesystem_watcher():
    """Test the filesystem watcher functionality"""

    # Create a vault directory for testing
    vault_path = Path("AI_Employee_Vault")
    drop_folder = vault_path / "Drop_Folder"
    drop_folder.mkdir(exist_ok=True)

    print(f"Test setup complete!")
    print(f"1. Vault path: {vault_path}")
    print(f"2. Drop folder: {drop_folder}")
    print(f"3. Needs_Action folder: {vault_path / 'Needs_Action'}")
    print()
    print("To test the filesystem watcher:")
    print(f"- Place any file (e.g., .txt, .pdf) in the {drop_folder} folder")
    print("- The AI Employee will detect it and move it to Needs_Action folder")
    print("- The orchestrator will process it and move it to Done folder")
    print()
    print("Starting orchestrator with the command:")
    print(f"python orchestrator.py {vault_path}")

if __name__ == "__main__":
    test_filesystem_watcher()