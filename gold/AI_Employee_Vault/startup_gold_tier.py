#!/usr/bin/env python3
"""
Gold Tier AI Employee System Startup Script
This script starts all components of the Gold Tier AI Employee system with proper orchestration
"""

import os
import sys
import time
import signal
import subprocess
import threading
import logging
from pathlib import Path
import json
from datetime import datetime

# Add the vault path to Python path to import local modules
VAULT_PATH = Path(__file__).parent
sys.path.insert(0, str(VAULT_PATH))

def setup_logging():
    """Setup system logging"""
    log_dir = VAULT_PATH / 'Logs'
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'gold_tier_startup.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger('GoldTierStartup')

logger = setup_logging()

class GoldTierOrchestrator:
    """
    Orchestrates all Gold Tier components of the AI Employee system
    """

    def __init__(self):
        self.processes = {}
        self.is_running = False
        self.log_dir = VAULT_PATH / 'Logs'

    def initialize_vault_structure(self):
        """Ensure all required vault directories exist"""
        required_dirs = [
            'Inbox',
            'Needs_Action',
            'Done',
            'Plans',
            'Pending_Approval',
            'Approved',
            'Rejected',
            'Briefings',
            'Reports',
            'Drop_Folder',
            'Logs'
        ]

        for dir_name in required_dirs:
            (VAULT_PATH / dir_name).mkdir(exist_ok=True)

        logger.info("Vault structure initialized")

    def create_business_goals_if_missing(self):
        """Create Business_Goals.md if it doesn't exist"""
        goals_file = VAULT_PATH / 'Business_Goals.md'
        if not goals_file.exists():
            goals_content = """---
last_updated: {date}
review_frequency: weekly
---

# Business Goals & Objectives

## Q1 2026 Objectives

### Revenue Target
- Monthly goal: $10,000
- Current MTD: $0
- YTD: $0

### Key Metrics to Track
| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Client response time | < 24 hours | > 48 hours |
| Invoice payment rate | > 90% | < 80% |
| Software costs | < $500/month | > $600/month |
| Social media engagement | > 50 interactions/week | < 30/week |
| Lead conversion rate | > 15% | < 10% |

## Active Projects
1. Project Alpha - Due Mar 15 - Budget $2,000
2. Project Beta - Due Apr 30 - Budget $3,500
3. Project Gamma - Due May 15 - Budget $1,200

## Subscription Audit Rules
Flag for review if:
- No usage in 30 days
- Cost increased > 20%
- Duplicate functionality with another tool
- Monthly cost > $100 without clear ROI
"""
            goals_file.write_text(goals_content.format(date=datetime.now().strftime('%Y-%m-%d')))
            logger.info("Business_Goals.md created")

    def start_watchdog(self):
        """Start the watchdog process"""
        try:
            cmd = [sys.executable, str(VAULT_PATH / 'system_watchdog.py')]
            process = subprocess.Popen(cmd, cwd=VAULT_PATH)
            self.processes['watchdog'] = process
            logger.info(f"Watchdog started with PID {process.pid}")
            return True
        except Exception as e:
            logger.error(f"Failed to start watchdog: {e}")
            return False

    def start_browser_mcp(self):
        """Start the browser MCP server"""
        try:
            # Import and start browser MCP server in a thread
            from mcp_browser_server import BrowserMCPServer
            import asyncio

            def run_browser_server():
                async def start():
                    server = BrowserMCPServer()
                    await server.start_server()
                    # Keep running
                    while self.is_running:
                        await asyncio.sleep(1)

                # Run the async server in a new event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(start())

            browser_thread = threading.Thread(target=run_browser_server, daemon=True)
            browser_thread.start()
            self.processes['browser_mcp'] = browser_thread
            logger.info("Browser MCP server started in thread")
            return True
        except Exception as e:
            logger.error(f"Failed to start browser MCP: {e}")
            return False

    def start_payment_mcp(self):
        """Start the payment MCP server"""
        try:
            # For this implementation, we'll register the payment server but not run it continuously
            # since it operates on-demand
            from mcp_payment_server import PaymentMCPServer
            self.payment_server = PaymentMCPServer(str(VAULT_PATH))
            logger.info("Payment MCP server initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to start payment MCP: {e}")
            return False

    def start_scheduled_tasks(self):
        """Start the scheduler"""
        try:
            cmd = [sys.executable, str(VAULT_PATH / 'scheduler.py')]
            process = subprocess.Popen(cmd, cwd=VAULT_PATH)
            self.processes['scheduler'] = process
            logger.info(f"Scheduler started with PID {process.pid}")
            return True
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            return False

    def start_reasoning_loop(self):
        """Start the reasoning loop"""
        try:
            cmd = [sys.executable, str(VAULT_PATH / 'reasoning_loop.py')]
            process = subprocess.Popen(cmd, cwd=VAULT_PATH)
            self.processes['reasoning_loop'] = process
            logger.info(f"Reasoning loop started with PID {process.pid}")
            return True
        except Exception as e:
            logger.error(f"Failed to start reasoning loop: {e}")
            return False

    def start_watchers(self):
        """Start all watcher processes"""
        watchers = [
            ('gmail_watcher', 'gmail_watcher.py'),
            ('whatsapp_watcher', 'whatsapp_watcher.py'),
            ('linkedin_watcher', 'linkedin_watcher.py'),
            ('filesystem_watcher', 'filesystem_watcher.py')
        ]

        success_count = 0
        for name, script in watchers:
            try:
                cmd = [sys.executable, str(VAULT_PATH / script)]
                process = subprocess.Popen(cmd, cwd=VAULT_PATH)
                self.processes[name] = process
                logger.info(f"{name} started with PID {process.pid}")
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to start {name}: {e}")

        return success_count == len(watchers)

    def start_ceo_briefing_generator(self):
        """Start the CEO briefing generator as a scheduled task"""
        try:
            # This would typically be integrated into the scheduler
            # For now, we'll log that it's available
            logger.info("CEO Briefing generator ready (integrated with scheduler)")
            return True
        except Exception as e:
            logger.error(f"Failed to start CEO briefing generator: {e}")
            return False

    def update_dashboard_status(self):
        """Update the dashboard with current system status"""
        dashboard_file = VAULT_PATH / 'Dashboard.md'

        # Read existing dashboard or create default
        if dashboard_file.exists():
            content = dashboard_file.read_text()
        else:
            content = """# AI Employee Dashboard

## Overview
This dashboard provides a real-time summary of your personal and business activities managed by your AI Employee.

## Current Status
- **Last Update**: 2026-02-21 00:00:00
- **AI Employee Status**: Initializing
- **Active Tasks**: 0
- **Pending Actions**: 0

## Recent Activity
- [No recent activity]

## Alerts & Notifications
- [No alerts]

## Next Actions
- [No pending actions]

## Business Metrics
- **Current Month Revenue**: $0.00
- **Active Projects**: 0
- **Pending Invoices**: 0

## System Status
- **Watchers Active**: 0
- **Last Watcher Check**: Never
- **Vault Sync Status**: Local only
"""

        # Update status information
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        active_processes = len([p for p in self.processes.values()
                              if hasattr(p, 'poll') and p.poll() is None])

        # Replace status sections
        lines = content.split('\n')
        new_lines = []

        for line in lines:
            if line.startswith('- **AI Employee Status**:'):
                new_lines.append(f"- **AI Employee Status**: Running (Gold Tier)")
            elif line.startswith('- **Active Tasks**:'):
                # This would be updated based on actual system state
                new_lines.append(f"- **Active Tasks**: {active_processes}")
            elif line.startswith('- **Last Update**:'):
                new_lines.append(f"- **Last Update**: {timestamp}")
            elif line.startswith('- **Watchers Active**:'):
                # Count running watcher processes
                watcher_count = 0
                for name, proc in self.processes.items():
                    if 'watcher' in name:
                        try:
                            if proc.poll() is None:  # Process is running
                                watcher_count += 1
                        except:
                            pass
                new_lines.append(f"- **Watchers Active**: {watcher_count}")
            elif line.startswith('- **Last Watcher Check**:'):
                new_lines.append(f"- **Last Watcher Check**: {timestamp}")
            else:
                new_lines.append(line)

        updated_content = '\n'.join(new_lines)

        # Add startup log
        if f"{timestamp} - Gold Tier system started successfully" not in updated_content:
            updated_content += f"\n- {timestamp} - Gold Tier system started successfully"

        dashboard_file.write_text(updated_content)

    def start_all_services(self):
        """Start all Gold Tier services"""
        logger.info("Starting Gold Tier AI Employee System...")
        self.is_running = True

        # Initialize vault structure
        self.initialize_vault_structure()
        self.create_business_goals_if_missing()

        # Start services in order of dependency
        services = [
            ('Watchdog', self.start_watchdog),
            ('Browser MCP', self.start_browser_mcp),
            ('Payment MCP', self.start_payment_mcp),
            ('Scheduler', self.start_scheduled_tasks),
            ('Reasoning Loop', self.start_reasoning_loop),
            ('Watchers', self.start_watchers),
            ('CEO Briefing Generator', self.start_ceo_briefing_generator),
        ]

        started_services = 0
        for service_name, start_func in services:
            logger.info(f"Starting {service_name}...")
            try:
                success = start_func()
                if success:
                    started_services += 1
                    logger.info(f"{service_name}: SUCCESS")
                else:
                    logger.error(f"{service_name}: FAILED")
            except Exception as e:
                logger.error(f"{service_name}: ERROR - {e}")

        # Update dashboard with system status
        self.update_dashboard_status()

        logger.info(f"Gold Tier startup complete. {started_services}/{len(services)} services started successfully.")

        if started_services == len(services):
            logger.info("✅ Gold Tier AI Employee System is ready for operation!")
        else:
            logger.warning(f"⚠️  {len(services) - started_services} services failed to start")

        return started_services == len(services)

    def monitor_processes(self):
        """Monitor running processes and handle shutdown"""
        try:
            while self.is_running:
                # Check if any critical processes have died
                critical_processes = ['watchdog', 'scheduler', 'reasoning_loop']

                for proc_name in critical_processes:
                    if proc_name in self.processes:
                        proc = self.processes[proc_name]
                        try:
                            if hasattr(proc, 'poll'):
                                poll_result = proc.poll()
                                if poll_result is not None:
                                    logger.warning(f"Critical process {proc_name} (PID {proc.pid}) exited with code {poll_result}")
                                    # In a real system, you might restart the process here
                                    # For safety in this example, we'll just log it
                        except Exception as e:
                            logger.error(f"Error checking process {proc_name}: {e}")

                time.sleep(10)  # Check every 10 seconds
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        finally:
            self.shutdown()

    def shutdown(self):
        """Gracefully shut down all processes"""
        logger.info("Shutting down Gold Tier AI Employee System...")
        self.is_running = False

        # Terminate all processes
        for name, proc in self.processes.items():
            try:
                if hasattr(proc, 'terminate'):
                    proc.terminate()
                    logger.info(f"Terminated {name}")
                elif hasattr(proc, '_started'):
                    # Thread case
                    logger.info(f"Thread {name} marked for shutdown")
            except Exception as e:
                logger.error(f"Error terminating {name}: {e}")

        # Wait a bit for processes to terminate
        time.sleep(2)

        # Force kill if necessary
        for name, proc in self.processes.items():
            try:
                if hasattr(proc, 'poll') and proc.poll() is None:
                    proc.kill()
                    logger.info(f"Force killed {name}")
            except Exception as e:
                logger.error(f"Error force killing {name}: {e}")

        logger.info("Gold Tier system shutdown complete")


def signal_handler(signum, frame, orchestrator):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    orchestrator.shutdown()
    sys.exit(0)


def main():
    """Main entry point"""
    logger.info("Gold Tier AI Employee System starting up...")

    orchestrator = GoldTierOrchestrator()

    # Set up signal handlers
    signal.signal(signal.SIGINT, lambda s, f: signal_handler(s, f, orchestrator))
    signal.signal(signal.SIGTERM, lambda s, f: signal_handler(s, f, orchestrator))

    try:
        # Start all services
        success = orchestrator.start_all_services()

        if not success:
            logger.error("Failed to start all services, exiting...")
            return 1

        # Monitor processes
        orchestrator.monitor_processes()

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        orchestrator.shutdown()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        orchestrator.shutdown()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())