"""
Simple workflow test to verify file movement works in a clean environment
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from skills.workflow_skill import move_file_to_needs_action, move_file_to_done, get_next_action_files
from pathlib import Path

def test_clean_workflow():
    print("Testing workflow with clean environment...")
    vault_path = "."

    # Create a new test file in Inbox
    inbox_path = Path(vault_path) / "Inbox"
    test_file = inbox_path / "clean_test_file.txt"

    # Write content to the test file
    test_file.write_text("Test content for clean workflow test")
    print(f"Created test file: {test_file}")

    # Check initial state
    print("Initial state:")
    print(f"  Inbox files: {len(list((Path(vault_path) / 'Inbox').glob('*')))}")
    print(f"  Needs_Action files: {len(list((Path(vault_path) / 'Needs_Action').glob('*')))}")
    print(f"  Done files: {len(list((Path(vault_path) / 'Done').glob('*')))}")

    # Move from Inbox to Needs_Action
    print(f"\nMoving {test_file.name} from Inbox to Needs_Action...")
    success = move_file_to_needs_action(vault_path, test_file)
    if success:
        print("  [PASS] Successfully moved to Needs_Action")
    else:
        print("  [FAIL] Failed to move to Needs_Action")
        return False

    # Check state after first move
    print("After Inbox -> Needs_Action:")
    print(f"  Inbox files: {len(list((Path(vault_path) / 'Inbox').glob('*')))}")
    print(f"  Needs_Action files: {len(list((Path(vault_path) / 'Needs_Action').glob('*')))}")

    # Get the file from Needs_Action and move to Done
    action_files = get_next_action_files(vault_path)
    if action_files:
        action_file = action_files[0]
        print(f"\nMoving {action_file.name} from Needs_Action to Done...")
        success = move_file_to_done(vault_path, action_file)
        if success:
            print("  [PASS] Successfully moved to Done")
        else:
            print("  [FAIL] Failed to move to Done")
            return False
    else:
        print("  No files found in Needs_Action")
        return False

    # Check final state
    print("Final state:")
    print(f"  Inbox files: {len(list((Path(vault_path) / 'Inbox').glob('*')))}")
    print(f"  Needs_Action files: {len(list((Path(vault_path) / 'Needs_Action').glob('*')))}")
    print(f"  Done files: {len(list((Path(vault_path) / 'Done').glob('*')))}")

    print("\n[SUCCESS] Workflow test completed successfully!")
    return True

if __name__ == "__main__":
    test_clean_workflow()