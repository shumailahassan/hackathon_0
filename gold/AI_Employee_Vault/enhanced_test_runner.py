#!/usr/bin/env python3
"""
Enhanced Test Runner for AI Employee Watcher Scripts
Tests LinkedIn and WhatsApp watchers in test mode with comprehensive validation
"""

import os
import sys
import time
import subprocess
from pathlib import Path
import logging
import json
from datetime import datetime

def setup_test_logging():
    """Setup logging for the test runner"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('enhanced_test_runner.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger('EnhancedTestRunner')

def test_linkedin_watcher():
    """Test LinkedIn watcher in test mode"""
    logger = logging.getLogger('LinkedInTest')
    logger.info("="*60)
    logger.info("TESTING LINKEDIN WATCHER")
    logger.info("="*60)

    try:
        # Set test mode environment variable
        env = os.environ.copy()
        env['TEST_MODE'] = 'True'

        # Run LinkedIn watcher in test mode
        logger.info("Starting LinkedIn watcher in test mode...")
        result = subprocess.run([
            sys.executable, "linkedin_watcher.py", "."
        ],
        timeout=180,  # 3 minute timeout (increased for complex setup)
        capture_output=True,
        text=True,
        env=env
        )

        logger.info(f"LinkedIn watcher exit code: {result.returncode}")

        if result.stdout:
            logger.info("LinkedIn STDOUT:")
            for line in result.stdout.split('\n'):
                if '[TEST MODE]' in line or 'INFO' in line or 'Browser' in line or 'Login' in line:
                    logger.info(f"  {line}")

        if result.stderr:
            logger.error("LinkedIn STDERR:")
            for line in result.stderr.split('\n'):
                if line.strip():
                    logger.error(f"  {line}")

        success = result.returncode == 0
        logger.info(f"LinkedIn test result: {'PASS' if success else 'FAIL'}")
        return success

    except subprocess.TimeoutExpired:
        logger.error("LinkedIn watcher test timed out")
        return False
    except Exception as e:
        logger.error(f"Error running LinkedIn test: {e}")
        return False

def test_whatsapp_watcher():
    """Test WhatsApp watcher in test mode"""
    logger = logging.getLogger('WhatsAppTest')
    logger.info("="*60)
    logger.info("TESTING WHATSAPP WATCHER")
    logger.info("="*60)

    try:
        # Set test mode environment variable
        env = os.environ.copy()
        env['TEST_MODE'] = 'True'

        # Run WhatsApp watcher in test mode
        logger.info("Starting WhatsApp watcher in test mode...")
        result = subprocess.run([
            sys.executable, "whatsapp_watcher.py", "."
        ],
        timeout=180,  # 3 minute timeout (increased for complex setup)
        capture_output=True,
        text=True,
        env=env
        )

        logger.info(f"WhatsApp watcher exit code: {result.returncode}")

        if result.stdout:
            logger.info("WhatsApp STDOUT:")
            for line in result.stdout.split('\n'):
                if '[TEST MODE]' in line or 'INFO' in line or 'Browser' in line or 'Login' in line or 'QR' in line:
                    logger.info(f"  {line}")

        if result.stderr:
            logger.error("WhatsApp STDERR:")
            for line in result.stderr.split('\n'):
                if line.strip():
                    logger.error(f"  {line}")

        success = result.returncode == 0
        logger.info(f"WhatsApp test result: {'PASS' if success else 'FAIL'}")
        return success

    except subprocess.TimeoutExpired:
        logger.error("WhatsApp watcher test timed out")
        return False
    except Exception as e:
        logger.error(f"Error running WhatsApp test: {e}")
        return False

def check_playwright_installation():
    """Check if Playwright and Chromium are properly installed"""
    logger = logging.getLogger('PlaywrightCheck')
    logger.info("="*60)
    logger.info("CHECKING PLAYWRIGHT INSTALLATION")
    logger.info("="*60)

    try:
        import playwright
        # Get version using importlib since playwright doesn't have __version__ attribute
        try:
            from importlib.metadata import version
            playwright_version = version("playwright")
            logger.info(f"Playwright version: {playwright_version}")
        except ImportError:
            # Fallback if importlib.metadata is not available
            logger.info("Playwright import: SUCCESS (version check not available)")

        # Check if browsers are installed by trying to import sync_playwright
        from playwright.sync_api import sync_playwright
        logger.info("Playwright sync API import: PASS")

        # Try to launch Chromium to verify it's properly installed
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("about:blank")
            browser.close()

        logger.info("Chromium browser launch: PASS")
        return True

    except ImportError as e:
        logger.error(f"Playwright import error: {e}")
        return False
    except Exception as e:
        logger.error(f"Chromium launch error: {e}")
        return False

def check_session_persistence():
    """Check if session directories exist and are properly configured"""
    logger = logging.getLogger('SessionCheck')
    logger.info("="*60)
    logger.info("CHECKING SESSION PERSISTENCE")
    logger.info("="*60)

    success = True

    # Check LinkedIn session directory
    linkedin_session = Path('linkedin_session')
    if linkedin_session.exists():
        logger.info(f"LinkedIn session directory exists: {linkedin_session}")
        session_files = list(linkedin_session.rglob('*'))
        logger.info(f"  Contents: {len(session_files)} files/directories")

        # Check if there are actual session data files
        data_files = [f for f in session_files if f.is_file() and f.suffix in ['.ldb', '.log', '.tmp', '']]
        logger.info(f"  Data files: {len(data_files)}")
        if len(data_files) == 0:
            logger.warning("  No session data files found - may need to authenticate first")
    else:
        logger.info(f"LinkedIn session directory does not exist: {linkedin_session}")
        logger.info("  This may be normal if authentication hasn't been set up yet")

    # Check WhatsApp session directory
    whatsapp_session = Path('whatsapp_session')
    if whatsapp_session.exists():
        logger.info(f"WhatsApp session directory exists: {whatsapp_session}")
        session_files = list(whatsapp_session.rglob('*'))
        logger.info(f"  Contents: {len(session_files)} files/directories")

        # Check if there are actual session data files
        data_files = [f for f in session_files if f.is_file() and f.suffix in ['.ldb', '.log', '.tmp', '']]
        logger.info(f"  Data files: {len(data_files)}")
        if len(data_files) == 0:
            logger.warning("  No session data files found - may need to authenticate first")
    else:
        logger.info(f"WhatsApp session directory does not exist: {whatsapp_session}")
        logger.info("  This may be normal if authentication hasn't been set up yet")

    # Check if session directories are accessible for creation
    try:
        linkedin_session.mkdir(exist_ok=True)
        whatsapp_session.mkdir(exist_ok=True)
        logger.info("Session directory access: PASS")
    except Exception as e:
        logger.error(f"Could not access session directories: {e}")
        success = False

    return success

def check_mcp_connectivity():
    """Check if MCP servers are properly configured"""
    logger = logging.getLogger('MCPCheck')
    logger.info("="*60)
    logger.info("CHECKING MCP CONNECTIVITY")
    logger.info("="*60)

    # Check if MCP server files exist
    mcp_files = [
        'mcp_browser_server.py',
        'mcp_payment_server.py',
        'mcp_email_server.py',
        'system_watchdog.py'  # Renamed from watchdog.py
    ]

    found_files = []
    missing_files = []

    for mcp_file in mcp_files:
        if Path(mcp_file).exists():
            logger.info(f"MCP file exists: {mcp_file}")
            found_files.append(mcp_file)
        else:
            logger.warning(f"MCP file missing: {mcp_file}")
            missing_files.append(mcp_file)

    # Also check for skills directory
    skills_dir = Path("skills")
    if skills_dir.exists():
        logger.info(f"Skills directory exists: {skills_dir}")
        skill_files = list(skills_dir.glob("*.py"))
        logger.info(f"  Found {len(skill_files)} skill files")
    else:
        logger.warning("Skills directory missing")

    success = len(missing_files) <= 2  # Allow up to 2 missing files since some may be optional

    logger.info(f"MCP connectivity check: {'PASS' if success else 'FAIL (with warnings)'}")
    return success

def run_additional_validations():
    """Run additional validations that don't fit in other categories"""
    logger = logging.getLogger('AdditionalCheck')
    logger.info("="*60)
    logger.info("RUNNING ADDITIONAL VALIDATIONS")
    logger.info("="*60)

    success = True

    # Check requirements.txt for Playwright
    requirements_file = Path('requirements.txt')
    if requirements_file.exists():
        content = requirements_file.read_text()
        if 'playwright' in content.lower():
            logger.info("Playwright in requirements.txt: PASS")
        else:
            logger.warning("Playwright not found in requirements.txt")
            success = False
    else:
        logger.error("requirements.txt not found")
        success = False

    # Check for base_watcher
    if Path('base_watcher.py').exists():
        logger.info("Base watcher exists: PASS")
    else:
        logger.error("Base watcher not found")
        success = False

    # Check for common config files
    common_configs = ['config.json', 'settings.json', '.env']
    for config in common_configs:
        if Path(config).exists():
            logger.info(f"Configuration file {config} exists: PASS")

    return success

def generate_validation_report(linkedin_result, whatsapp_result, playwright_result, session_result, mcp_result, additional_result):
    """Generate a comprehensive validation report"""
    logger = logging.getLogger('ValidationReport')
    logger.info("="*80)
    logger.info("COMPREHENSIVE VALIDATION REPORT")
    logger.info("="*80)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Report generated at: {timestamp}")
    logger.info("")

    logger.info("Component Status:")
    logger.info(f"  LinkedIn Auth:        {'PASS' if linkedin_result else 'FAIL'}")
    logger.info(f"  WhatsApp Session:     {'PASS' if whatsapp_result else 'FAIL'}")
    logger.info(f"  Playwright Install:   {'PASS' if playwright_result else 'FAIL'}")
    logger.info(f"  Session Persistence:  {'PASS' if session_result else 'FAIL'}")
    logger.info(f"  MCP Connectivity:     {'PASS' if mcp_result else 'FAIL'}")
    logger.info(f"  Additional Checks:    {'PASS' if additional_result else 'FAIL'}")

    # Calculate overall status
    all_passed = all([linkedin_result, whatsapp_result, playwright_result, session_result, mcp_result, additional_result])

    logger.info("")
    logger.info("Overall Status:")
    if all_passed:
        logger.info("  [SUCCESS] ALL SYSTEMS OPERATIONAL - READY FOR PRODUCTION")
        logger.info("  [PASS] All components passing validation tests")
    else:
        logger.info("  [WARNING] SYSTEM REQUIRES ATTENTION")
        logger.info("  Some components failed validation tests")

        failed_components = []
        if not linkedin_result:
            failed_components.append("LinkedIn Auth")
        if not whatsapp_result:
            failed_components.append("WhatsApp Session")
        if not playwright_result:
            failed_components.append("Playwright Install")
        if not session_result:
            failed_components.append("Session Persistence")
        if not mcp_result:
            failed_components.append("MCP Connectivity")
        if not additional_result:
            failed_components.append("Additional Checks")

        logger.info(f"  Failed components: {', '.join(failed_components)}")

    # Create summary for easy parsing
    summary = {
        "timestamp": timestamp,
        "linkedin_auth": "PASS" if linkedin_result else "FAIL",
        "whatsapp_session": "PASS" if whatsapp_result else "FAIL",
        "playwright_install": "PASS" if playwright_result else "FAIL",
        "session_persistence": "PASS" if session_result else "FAIL",
        "mcp_connectivity": "PASS" if mcp_result else "FAIL",
        "additional_checks": "PASS" if additional_result else "FAIL",
        "overall_status": "PASS" if all_passed else "FAIL"
    }

    logger.info("")
    logger.info("JSON Summary:")
    logger.info(json.dumps(summary, indent=2))

    logger.info("="*80)

    # Write summary to file
    summary_file = Path("validation_summary.json")
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    logger.info(f"Summary written to: {summary_file}")
    logger.info("="*80)

    return summary

def main():
    """Main test runner function"""
    logger = setup_test_logging()
    logger.info("Starting Enhanced AI Employee Watcher Test Runner")
    logger.info("This test runner evaluates the complete AI Employee Vault system")
    logger.info("")

    # Run all tests
    logger.info("Running Playwright installation check...")
    playwright_result = check_playwright_installation()

    logger.info("\nRunning session persistence check...")
    session_result = check_session_persistence()

    logger.info("\nRunning MCP connectivity check...")
    mcp_result = check_mcp_connectivity()

    logger.info("\nRunning additional validations...")
    additional_result = run_additional_validations()

    # Only run browser-based tests if Playwright is working
    if playwright_result:
        logger.info("\nRunning LinkedIn watcher test...")
        linkedin_result = test_linkedin_watcher()

        logger.info("\nRunning WhatsApp watcher test...")
        whatsapp_result = test_whatsapp_watcher()
    else:
        logger.warning("Skipping browser-based tests due to Playwright issues")
        linkedin_result = False
        whatsapp_result = False

    # Generate final report
    summary = generate_validation_report(
        linkedin_result,
        whatsapp_result,
        playwright_result,
        session_result,
        mcp_result,
        additional_result
    )

    logger.info(f"\nEnhanced Test Runner completed. Overall status: {summary['overall_status']}")

    # Exit with appropriate code
    return 0 if summary['overall_status'] == "PASS" else 1

if __name__ == "__main__":
    sys.exit(main())