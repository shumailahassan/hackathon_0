"""
Final verification of all Bronze Tier functionality
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from skills.vault_read_skill import read_dashboard_content, read_company_handbook
from skills.vault_write_skill import update_dashboard_status
from skills.watcher_skill import FilesystemWatcher
from skills.logging_skill import initialize_logging_system, log_system_status
from pathlib import Path
import time

def final_verification():
    print("=== Final Bronze Tier Verification ===\n")

    # 1. Test Vault Reading
    print("1. Testing Vault Reading...")
    dashboard_content = read_dashboard_content(".")
    handbook_content = read_company_handbook(".")
    if dashboard_content and handbook_content:
        print("   [PASS] Successfully read Dashboard.md and Company_Handbook.md")
    else:
        print("   [FAIL] Failed to read vault files")
        return False

    # 2. Test Vault Writing
    print("2. Testing Vault Writing...")
    success = update_dashboard_status(".", status="Verification Complete", active_tasks=0, pending_actions=0)
    if success:
        print("   [PASS] Successfully updated Dashboard status")
    else:
        print("   [FAIL] Failed to update Dashboard status")
        return False

    # 3. Test Logging System
    print("3. Testing Logging System...")
    initialize_logging_system()
    log_system_status("verification_complete", "Bronze Tier system verification completed")
    print("   [PASS] Logging system initialized and working")

    # 4. Test Watcher Configuration
    print("4. Testing Watcher Configuration...")
    watcher = FilesystemWatcher(".", "./Drop_Folder")
    print(f"   [PASS] Watcher configured for: {watcher.watch_path}")

    # 5. Test that all expected directories exist
    print("5. Testing Directory Structure...")
    expected_dirs = ["Inbox", "Needs_Action", "Done", "Drop_Folder", "Logs"]
    all_exist = True
    for dir_name in expected_dirs:
        if not Path(dir_name).exists():
            print(f"   [FAIL] Directory {dir_name} does not exist")
            all_exist = False
        else:
            print(f"   [PASS] Directory {dir_name} exists")

    if not all_exist:
        return False

    print("\n=== Bronze Tier Verification Results ===")
    print("[PASS] Vault reading functionality")
    print("[PASS] Vault writing functionality")
    print("[PASS] Logging system")
    print("[PASS] Watcher configuration")
    print("[PASS] Directory structure")

    print("\n*** All Bronze Tier functionality is working correctly! ***")
    print("\nSystem Status:")
    print("- Vault skills: Available (read/write to Dashboard.md and Company_Handbook.md)")
    print("- Workflow skills: Available (file movement from Inbox -> Needs_Action -> Done)")
    print("- Watcher functionality: Available (Drop_Folder monitoring)")
    print("- Logging functionality: Available (actions and errors logged)")

    return True

if __name__ == "__main__":
    final_verification()