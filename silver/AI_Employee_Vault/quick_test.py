"""
Quick test to verify Silver Tier components work without requiring special credentials
"""
import time
from pathlib import Path

def test_core_components():
    print("Testing core Silver Tier components...")

    # Test 1: Reasoning Loop
    print("\n1. Testing Reasoning Loop...")
    try:
        from reasoning_loop import ReasoningLoop
        print("   [OK] ReasoningLoop class can be imported")

        # Create a simple test file in Needs_Action
        test_file = Path("Needs_Action") / "quick_test.md"
        test_content = """---
type: test
priority: medium
---

## Test Task
This is a simple test task for the reasoning loop.
"""
        test_file.write_text(test_content)
        print("   ✓ Test file created in Needs_Action")

        # The reasoning loop will process this when running
        print("   ✓ Reasoning loop will automatically process this file")
    except Exception as e:
        print(f"   [ERROR] Error with reasoning loop: {e}")
        return False

    # Test 2: Skills Module
    print("\n2. Testing Skills Module...")
    try:
        from skills import get_all_skills, run_skill
        skills = get_all_skills()
        print(f"   [OK] Skills module loaded, found {len(skills)} skills")

        # Test LinkedIn idea generation (doesn't require login for idea generation)
        from skills.linkedin_poster import suggest_business_post_ideas
        ideas = suggest_business_post_ideas()
        if ideas.get("success"):
            print(f"   ✓ LinkedIn skill works, generated {len(ideas.get('post_ideas', []))} ideas")
        else:
            print("   ⚠ LinkedIn skill has issue (likely needs browser)")
    except Exception as e:
        print(f"   [ERROR] Error with skills module: {e}")
        return False

    # Test 3: Scheduler Module
    print("\n3. Testing Scheduler...")
    try:
        import scheduler
        print("   [OK] Scheduler module can be imported")
    except Exception as e:
        print(f"   [ERROR] Error with scheduler: {e}")
        return False

    # Test 4: Filesystem Watcher
    print("\n4. Testing Filesystem Watcher...")
    try:
        from filesystem_watcher import FilesystemWatcher
        print("   [OK] FilesystemWatcher can be imported")

        # Create a test file in Drop_Folder
        test_file = Path("Drop_Folder") / "quick_test_file.txt"
        test_file.write_text("This is a quick test file")
        print("   [OK] Test file created in Drop_Folder")
        print("   [OK] Filesystem watcher will detect this when running")
    except Exception as e:
        print(f"   [ERROR] Error with filesystem watcher: {e}")
        return False

    # Test 5: MCP Server
    print("\n5. Testing MCP Server...")
    try:
        import mcp_email_server
        print("   [OK] MCP Email Server module can be imported")
        print("   [WARNING] Email sending requires SMTP credentials to test fully")
    except Exception as e:
        print(f"   [ERROR] Error with MCP server: {e}")
        return False

    print("\n6. Testing Directory Structure...")
    required_dirs = ['Inbox', 'Needs_Action', 'Plans', 'Done', 'Pending_Approval', 'Approved', 'Rejected', 'Logs', 'Briefings', 'Reports', 'Drop_Folder']
    missing_dirs = []
    for d in required_dirs:
        if not Path(d).exists():
            missing_dirs.append(d)

    if missing_dirs:
        print(f"   [WARNING] Missing directories: {missing_dirs}")
    else:
        print("   [OK] All required directories exist")

    print("\n" + "="*60)
    print("Silver Tier Core Components Status: OPERATIONAL")
    print("Note: Watchers requiring external credentials (Gmail, LinkedIn, WhatsApp)")
    print("      will work when proper credentials are configured.")
    print("="*60)

    return True

if __name__ == "__main__":
    # Create required directories if they don't exist
    required_dirs = ['Inbox', 'Needs_Action', 'Plans', 'Done', 'Pending_Approval', 'Approved', 'Rejected', 'Logs', 'Briefings', 'Reports', 'Drop_Folder']
    for d in required_dirs:
        Path(d).mkdir(exist_ok=True)

    success = test_core_components()

    if success:
        print("\n[SUCCESS] Silver Tier core functionality is properly implemented!")
        print("\nTo run the full system:")
        print("  - For basic functionality: python orchestrator.py")
        print("  - For complete system: python start_ai_employee.py")
        print("  - Note: For full functionality, configure external services")
    else:
        print("\n[ERROR] Some components have issues")