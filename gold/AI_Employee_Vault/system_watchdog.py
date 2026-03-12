"""
Watchdog Process for AI Employee System
Monitors critical services and ensures they remain operational with auto-restart capabilities
"""

import time
import subprocess
import psutil
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import signal
import sys

class Watchdog:
    """
    Watchdog process that monitors AI Employee services and restarts them if they fail
    """

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.processes_file = self.vault_path / 'processes.json'
        self.logs = self.vault_path / 'Logs'
        self.logs.mkdir(exist_ok=True)

        # Setup logging
        self.logger = logging.getLogger('Watchdog')
        handler = logging.FileHandler(self.logs / 'watchdog.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

        # Define the services to monitor
        self.services = {
            'gmail_watcher': {
                'command': ['python', str(self.vault_path / 'gmail_watcher.py')],
                'restart_attempts': 0,
                'max_restarts': 5,
                'restart_window': 300,  # 5 minutes
                'pid': None
            },
            'whatsapp_watcher': {
                'command': ['python', str(self.vault_path / 'whatsapp_watcher.py')],
                'restart_attempts': 0,
                'max_restarts': 5,
                'restart_window': 300,
                'pid': None
            },
            'linkedin_watcher': {
                'command': ['python', str(self.vault_path / 'linkedin_watcher.py')],
                'restart_attempts': 0,
                'max_restarts': 5,
                'restart_window': 300,
                'pid': None
            },
            'scheduler': {
                'command': ['python', str(self.vault_path / 'scheduler.py')],
                'restart_attempts': 0,
                'max_restarts': 5,
                'restart_window': 300,
                'pid': None
            },
            'reasoning_loop': {
                'command': ['python', str(self.vault_path / 'reasoning_loop.py')],
                'restart_attempts': 0,
                'max_restarts': 5,
                'restart_window': 300,
                'pid': None
            }
        }

        # Track restart times for rate limiting
        self.restart_times = {service: [] for service in self.services}

        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, shutting down watchdog...")
        self.shutdown()
        sys.exit(0)

    def is_process_running(self, pid: int) -> bool:
        """Check if a process is still running"""
        try:
            process = psutil.Process(pid)
            return process.is_running() and process.status() != psutil.STATUS_ZOMBIE
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False

    def save_service_state(self):
        """Save current service state to file"""
        state = {}
        for service, info in self.services.items():
            state[service] = {
                'pid': info['pid'],
                'restart_attempts': info['restart_attempts'],
                'last_restart': time.time() if info['pid'] else None
            }

        with open(self.processes_file, 'w') as f:
            json.dump(state, f, indent=2)

    def load_service_state(self):
        """Load service state from file"""
        if self.processes_file.exists():
            try:
                with open(self.processes_file, 'r') as f:
                    state = json.load(f)

                for service, info in state.items():
                    if service in self.services:
                        self.services[service]['pid'] = info.get('pid')
                        self.services[service]['restart_attempts'] = info.get('restart_attempts', 0)
            except Exception as e:
                self.logger.error(f"Failed to load service state: {e}")

    def cleanup_old_restarts(self, service: str):
        """Remove restart attempts that are outside the time window"""
        current_time = time.time()
        self.restart_times[service] = [
            t for t in self.restart_times[service]
            if current_time - t < self.services[service]['restart_window']
        ]

    def can_restart_service(self, service: str) -> bool:
        """Check if we can restart a service based on rate limiting"""
        self.cleanup_old_restarts(service)
        return len(self.restart_times[service]) < self.services[service]['max_restarts']

    def restart_service(self, service: str) -> bool:
        """Restart a specific service"""
        if not self.can_restart_service(service):
            self.logger.error(f"Too many restart attempts for {service}, not restarting")
            return False

        try:
            # Log restart attempt
            self.restart_times[service].append(time.time())
            self.services[service]['restart_attempts'] += 1

            # Start the process
            command = self.services[service]['command']
            process = subprocess.Popen(command, cwd=self.vault_path)

            # Update service info
            self.services[service]['pid'] = process.pid
            self.logger.info(f"Restarted {service} with PID {process.pid}")

            # Notify human
            self.notify_human(f"{service} was restarted after failure")

            return True
        except Exception as e:
            self.logger.error(f"Failed to restart {service}: {e}")
            return False

    def check_and_restart_services(self):
        """Check all services and restart any that have failed"""
        for service, info in self.services.items():
            pid = info['pid']

            if pid is not None:
                # Check if the process is still running
                if not self.is_process_running(pid):
                    self.logger.warning(f"{service} (PID {pid}) has stopped, restarting...")
                    self.restart_service(service)
            else:
                # Service not running, try to start it
                self.logger.info(f"Starting {service}...")
                self.restart_service(service)

    def notify_human(self, message: str):
        """Log a notification that requires human attention"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Add to Dashboard
        dashboard_file = self.vault_path / 'Dashboard.md'
        if dashboard_file.exists():
            content = dashboard_file.read_text()
            new_line = f"- {timestamp} - {message}\n"

            # Find the alerts section and add notification
            lines = content.split('\n')
            new_content = []
            alerts_section_found = False

            for line in lines:
                if line.strip() == '## Alerts & Notifications':
                    new_content.append(line)
                    new_content.append(f"- {timestamp} - {message}")
                    alerts_section_found = True
                elif line.strip().startswith('## ') and alerts_section_found:
                    # We've moved past the alerts section, add the new alert here too to ensure it's visible
                    new_content.append(f"- {timestamp} - {message}")
                    new_content.append(line)
                    alerts_section_found = False  # Reset flag
                else:
                    new_content.append(line)

            # If no alerts section was found, add it at the end
            if not alerts_section_found:
                content = '\n'.join(new_content)
                if not content.strip().endswith(f"- {timestamp} - {message}"):
                    content += f"\n- {timestamp} - {message}"
                dashboard_file.write_text(content)

    def check_disk_space(self) -> Dict[str, Any]:
        """Check disk space and log warnings if getting low"""
        try:
            disk_usage = psutil.disk_usage(self.vault_path)
            free_gb = disk_usage.free / (1024 ** 3)
            total_gb = disk_usage.total / (1024 ** 3)
            percent_used = (disk_usage.used / disk_usage.total) * 100

            result = {
                'free_gb': round(free_gb, 2),
                'total_gb': round(total_gb, 2),
                'percent_used': round(percent_used, 2),
                'status': 'warning' if percent_used > 80 else 'ok'
            }

            if percent_used > 90:
                self.logger.error(f"Disk usage critical: {percent_used:.1f}% used")
                self.notify_human(f"CRITICAL: Disk usage at {percent_used:.1f}%, please free up space")
            elif percent_used > 80:
                self.logger.warning(f"Disk usage high: {percent_used:.1f}% used")
                self.notify_human(f"WARNING: Disk usage at {percent_used:.1f}%")

            return result
        except Exception as e:
            self.logger.error(f"Failed to check disk space: {e}")
            return {'error': str(e)}

    def check_system_resources(self) -> Dict[str, Any]:
        """Check system resources and log warnings if needed"""
        try:
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Check memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # Check if any process is consuming too many resources
            high_cpu_processes = []
            high_memory_processes = []

            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if proc.info['cpu_percent'] > 50:  # High CPU usage
                        high_cpu_processes.append(proc.info)
                    if proc.info['memory_percent'] > 10:  # High memory usage
                        high_memory_processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass  # Process might have terminated

            result = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'high_cpu_processes': high_cpu_processes[:5],  # Limit to top 5
                'high_memory_processes': high_memory_processes[:5],
                'status': 'ok'
            }

            if cpu_percent > 90:
                self.logger.warning(f"High CPU usage: {cpu_percent}%")
                result['status'] = 'warning'

            if memory_percent > 90:
                self.logger.warning(f"High memory usage: {memory_percent}%")
                result['status'] = 'warning'

            return result
        except Exception as e:
            self.logger.error(f"Failed to check system resources: {e}")
            return {'error': str(e)}

    def run_health_check(self):
        """Run comprehensive health check"""
        disk_check = self.check_disk_space()
        resource_check = self.check_system_resources()

        # Log results
        self.logger.info(f"Health check: Disk - {disk_check}, Resources - {resource_check}")

    def shutdown(self):
        """Gracefully shut down the watchdog"""
        self.logger.info("Watchdog shutting down...")
        self.save_service_state()

    def run(self):
        """Main watchdog loop"""
        self.logger.info("Watchdog starting up...")
        self.load_service_state()

        try:
            while True:
                # Check services
                self.check_and_restart_services()

                # Run health checks periodically (every 10 minutes)
                current_time = int(time.time())
                if current_time % 600 == 0:  # Every 10 minutes
                    self.run_health_check()

                # Save state periodically
                if current_time % 300 == 0:  # Every 5 minutes
                    self.save_service_state()

                # Sleep for 30 seconds before next check
                time.sleep(30)

        except KeyboardInterrupt:
            self.logger.info("Watchdog interrupted by user")
        except Exception as e:
            self.logger.error(f"Watchdog error: {e}")
        finally:
            self.shutdown()


# If this script is run directly, start the watchdog
if __name__ == "__main__":
    import os
    vault_path = os.getenv('VAULT_PATH', '.')
    watchdog = Watchdog(vault_path)
    watchdog.run()