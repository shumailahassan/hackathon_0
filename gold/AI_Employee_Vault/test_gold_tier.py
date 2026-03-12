"""
Comprehensive test suite for Gold Tier AI Employee Implementation
Tests all major components: audit system, MCP servers, watchdog, and CEO briefings
"""

import unittest
import tempfile
import shutil
import os
import time
from pathlib import Path
import json
from datetime import datetime, timedelta

from audit_logic import BusinessAuditor
from mcp_browser_server import BrowserMCPServer
from mcp_payment_server import PaymentMCPServer
from system_watchdog import Watchdog


class TestGoldTierComponents(unittest.TestCase):
    """Test class for Gold Tier functionality"""

    def setUp(self):
        """Set up test environment"""
        # Create a temporary vault for testing
        self.test_vault = Path(tempfile.mkdtemp())

        # Create necessary directories
        (self.test_vault / 'Pending_Approval').mkdir(exist_ok=True)
        (self.test_vault / 'Approved').mkdir(exist_ok=True)
        (self.test_vault / 'Rejected').mkdir(exist_ok=True)
        (self.test_vault / 'Logs').mkdir(exist_ok=True)
        (self.test_vault / 'Inbox').mkdir(exist_ok=True)
        (self.test_vault / 'Needs_Action').mkdir(exist_ok=True)
        (self.test_vault / 'Done').mkdir(exist_ok=True)
        (self.test_vault / 'Plans').mkdir(exist_ok=True)

    def tearDown(self):
        """Clean up after tests"""
        # Try to remove the test directory, handling permission errors
        try:
            shutil.rmtree(self.test_vault)
        except PermissionError:
            # If we can't delete due to open files, just pass
            pass

    def test_business_auditor_basic_functionality(self):
        """Test basic business auditor functionality"""
        auditor = BusinessAuditor(str(self.test_vault))

        # Sample transaction
        transaction = {
            'description': 'Adobe Creative Cloud subscription',
            'amount': 52.99,
            'date': '2026-02-22T10:30:00Z',
            'merchant': 'Adobe'
        }

        result = auditor.analyze_transaction(transaction)
        self.assertEqual(result['type'], 'subscription')
        self.assertEqual(result['name'], 'Adobe Creative Cloud')
        self.assertEqual(result['amount'], 52.99)

    def test_business_auditor_transaction_classification(self):
        """Test transaction classification"""
        auditor = BusinessAuditor(str(self.test_vault))

        # Test revenue transaction
        revenue_transaction = {
            'description': 'Payment received from Client A for project work',
            'amount': 2500.00,
            'date': '2026-02-23T14:15:00Z',
            'merchant': 'Client A'
        }

        result = auditor.analyze_transaction(revenue_transaction)
        self.assertIn(result['type'], ['revenue', 'general'])
        self.assertEqual(result['amount'], 2500.00)

        # Test general transaction
        general_transaction = {
            'description': 'Gas station purchase',
            'amount': 45.30,
            'date': '2026-02-24T09:30:00Z',
            'merchant': 'Shell Gas'
        }

        result = auditor.analyze_transaction(general_transaction)
        self.assertIsNotNone(result['amount'])

    def test_weekly_summary_generation(self):
        """Test weekly summary generation"""
        auditor = BusinessAuditor(str(self.test_vault))

        # Sample transactions
        transactions = [
            {
                'description': 'Adobe Creative Cloud subscription',
                'amount': 52.99,
                'date': '2026-02-22T10:30:00Z',
                'merchant': 'Adobe'
            },
            {
                'description': 'Payment received from Client A',
                'amount': 2500.00,
                'date': '2026-02-23T14:15:00Z',
                'merchant': 'Client A'
            },
            {
                'description': 'Office supplies purchase',
                'amount': 85.50,
                'date': '2026-02-24T10:00:00Z',
                'merchant': 'Staples'
            }
        ]

        summary = auditor.generate_weekly_summary(
            transactions,
            '2026-02-22',
            '2026-02-28'
        )

        # Check that revenue and expenses are calculated
        self.assertGreaterEqual(summary['revenue']['total'], 2500.00)
        self.assertGreaterEqual(summary['expenses']['total'], 52.99 + 85.50)

        # Check that revenue breakdown contains Client A
        self.assertIn('Client A', summary['revenue']['breakdown'])

    def test_ceo_briefing_generation(self):
        """Test CEO briefing generation"""
        auditor = BusinessAuditor(str(self.test_vault))

        transactions = [
            {
                'description': 'Adobe Creative Cloud subscription',
                'amount': 52.99,
                'date': '2026-02-22T10:30:00Z',
                'merchant': 'Adobe'
            },
            {
                'description': 'Payment received from Client A',
                'amount': 2500.00,
                'date': '2026-02-23T14:15:00Z',
                'merchant': 'Client A'
            }
        ]

        summary = auditor.generate_weekly_summary(
            transactions,
            '2026-02-22',
            '2026-02-28'
        )
        briefing = auditor.generate_ceo_briefing(summary)

        # Check that briefing contains expected sections
        self.assertIn('# Monday Morning CEO Briefing', briefing)
        self.assertIn('## Revenue', briefing)
        self.assertIn('## Expenses', briefing)
        self.assertIn('Client A', briefing)

    def test_subscription_audit(self):
        """Test subscription audit functionality"""
        auditor = BusinessAuditor(str(self.test_vault))

        # Simulate usage for a subscription
        current_time = datetime.now()
        old_time = (current_time - timedelta(days=35)).isoformat()  # 35 days ago

        # Add usage data to simulate inactive subscription
        auditor.subscription_usage['Notion'] = [old_time]

        issues = auditor.identify_subscription_issues()

        # Check that inactive subscription is detected
        inactive_found = False
        for issue in issues:
            if issue['issue_type'] == 'inactive_subscription' and issue['name'] == 'Notion':
                inactive_found = True
                break

        self.assertTrue(inactive_found, "Should detect inactive Notion subscription")

    def test_payment_mcp_creation(self):
        """Test payment MCP server functionality"""
        server = PaymentMCPServer(str(self.test_vault))

        payment_data = {
            'amount': 250.00,
            'recipient': 'Client A',
            'reason': 'Payment for completed project work',
            'description': 'Final payment for Project Alpha',
            'category': 'Client Payment',
            'reference': 'INV-2026-001',
            'method': 'ACH Transfer'
        }

        result = server.handle_payment_request(payment_data)

        # Should create an approval request
        self.assertEqual(result['status'], 'approval_created')
        self.assertIn('Payment request created', result['message'])

    def test_payee_verification(self):
        """Test payee verification functionality"""
        server = PaymentMCPServer(str(self.test_vault))

        # Test known payee
        result = server.verify_payee("Client A")
        self.assertTrue(result['success'])
        self.assertIn(result['recipient'], ['Client A'])

        # Test unknown payee
        result = server.verify_payee("Unknown Company")
        self.assertTrue(result['success'])

    def test_payment_status_check(self):
        """Test payment status checking"""
        server = PaymentMCPServer(str(self.test_vault))

        # Test with a non-existent payment ID
        result = server.get_payment_status("FAKE1234")
        self.assertTrue(result['success'])
        self.assertEqual(result['status'], 'unknown')

    def test_watchdog_initialization(self):
        """Test watchdog initialization"""
        watchdog = Watchdog(str(self.test_vault))

        # Check that services are defined
        self.assertIn('gmail_watcher', watchdog.services)
        self.assertIn('whatsapp_watcher', watchdog.services)
        self.assertIn('linkedin_watcher', watchdog.services)
        self.assertIn('scheduler', watchdog.services)
        self.assertIn('reasoning_loop', watchdog.services)

        # Check that directories exist
        self.assertTrue((self.test_vault / 'Logs').exists())

    def test_file_state_management(self):
        """Test that watchdog can save and load state"""
        watchdog = Watchdog(str(self.test_vault))

        # Set some mock state
        watchdog.services['gmail_watcher']['pid'] = 12345
        watchdog.services['gmail_watcher']['restart_attempts'] = 2

        # Save state
        watchdog.save_service_state()

        # Create new watchdog instance
        watchdog2 = Watchdog(str(self.test_vault))

        # Load state
        watchdog2.load_service_state()

        # Check that state was loaded
        self.assertEqual(watchdog2.services['gmail_watcher']['pid'], 12345)
        self.assertEqual(watchdog2.services['gmail_watcher']['restart_attempts'], 2)

    def test_restarts_rate_limiting(self):
        """Test that restart rate limiting works"""
        watchdog = Watchdog(str(self.test_vault))

        # Add multiple restarts quickly
        for i in range(6):  # More than max_restarts
            watchdog.restart_times['gmail_watcher'].append(time.time())

        # Check that rate limiting works
        can_restart = watchdog.can_restart_service('gmail_watcher')
        self.assertFalse(can_restart, "Should not allow restart after exceeding limit")


class TestIntegration(unittest.TestCase):
    """Integration tests for Gold Tier components"""

    def setUp(self):
        """Set up test environment"""
        self.test_vault = Path(tempfile.mkdtemp())

        # Create necessary directories
        (self.test_vault / 'Pending_Approval').mkdir(exist_ok=True)
        (self.test_vault / 'Approved').mkdir(exist_ok=True)
        (self.test_vault / 'Rejected').mkdir(exist_ok=True)
        (self.test_vault / 'Logs').mkdir(exist_ok=True)
        (self.test_vault / 'Inbox').mkdir(exist_ok=True)
        (self.test_vault / 'Needs_Action').mkdir(exist_ok=True)
        (self.test_vault / 'Done').mkdir(exist_ok=True)
        (self.test_vault / 'Plans').mkdir(exist_ok=True)

    def tearDown(self):
        """Clean up after tests"""
        # Try to remove the test directory, handling permission errors
        try:
            shutil.rmtree(self.test_vault)
        except PermissionError:
            # If we can't delete due to open files, just pass
            pass

    def test_complete_workflow(self):
        """Test a complete workflow: transaction -> audit -> briefing"""
        # 1. Create auditor and process transactions
        auditor = BusinessAuditor(str(self.test_vault))

        transactions = [
            {
                'description': 'Adobe Creative Cloud subscription',
                'amount': 52.99,
                'date': '2026-02-22T10:30:00Z',
                'merchant': 'Adobe'
            },
            {
                'description': 'Payment received from Client A',
                'amount': 2500.00,
                'date': '2026-02-23T14:15:00Z',
                'merchant': 'Client A'
            }
        ]

        # 2. Generate summary
        summary = auditor.generate_weekly_summary(
            transactions,
            '2026-02-22',
            '2026-02-28'
        )

        # 3. Generate CEO briefing
        briefing = auditor.generate_ceo_briefing(summary)

        # 4. Verify briefing content
        self.assertIn('# Monday Morning CEO Briefing', briefing)
        self.assertIn('2500.00', briefing)  # Revenue amount should appear
        self.assertIn('Adobe', briefing)    # Expense should appear

    def test_payment_approval_workflow(self):
        """Test the complete payment approval workflow"""
        server = PaymentMCPServer(str(self.test_vault))

        # 1. Create a payment request
        payment_data = {
            'amount': 250.00,
            'recipient': 'Vendor X',
            'reason': 'Monthly service fee',
            'description': 'Payment for consulting services',
            'category': 'Business Service',
            'reference': 'INV-001',
            'method': 'Wire Transfer'
        }

        result = server.handle_payment_request(payment_data)

        # 2. Verify approval was created
        self.assertEqual(result['status'], 'approval_created')
        self.assertIn('awaiting approval', result['message'].lower())

        # 3. Check that approval file exists
        import glob
        approval_files = list(glob.glob(str(self.test_vault / 'Pending_Approval' / '*PAYMENT*.md')))
        self.assertGreater(len(approval_files), 0, "Should have created a payment approval file")

        # 4. Check content of approval file
        approval_content = Path(approval_files[0]).read_text()
        self.assertIn('250.00', approval_content)
        self.assertIn('Vendor X', approval_content)
        self.assertIn('approval_request', approval_content)


def run_tests():
    """Run all tests and return results"""
    # Create test suite
    test_suite = unittest.TestSuite()

    # Add all test cases
    test_suite.addTest(unittest.makeSuite(TestGoldTierComponents))
    test_suite.addTest(unittest.makeSuite(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    return result


if __name__ == '__main__':
    print("Running Gold Tier Test Suite...")
    print("=" * 50)

    result = run_tests()

    print("=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\nFailures:")
        for test, trace in result.failures:
            print(f"  {test}: {trace}")

    if result.errors:
        print("\nErrors:")
        for test, trace in result.errors:
            print(f"  {test}: {trace}")

    if result.wasSuccessful():
        print("\n[PASS] All tests passed!")
    else:
        print("\n[FAIL] Some tests failed!")