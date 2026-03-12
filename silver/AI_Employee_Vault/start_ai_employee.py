#!/usr/bin/env python3
"""
Starting script for the complete AI Employee system
This script starts all components of the Silver Tier AI Employee
"""

import os
import sys
import subprocess
import threading
import time
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_employee_startup.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def start_component(name: str, cmd: list, cwd: str = None):
    """Start a component as a subprocess"""
    try:
        logger.info(f"Starting {name}...")
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd
        )

        # Store process info
        return {
            'name': name,
            'process': process,
            'cmd': ' '.join(cmd)
        }
    except Exception as e:
        logger.error(f"Failed to start {name}: {e}")
        return None

def monitor_process(name: str, process):
    """Monitor a process and restart if needed"""
    while True:
        if process.poll() is not None:
            logger.warning(f"{name} exited with code: {process.returncode}")

            # Restart after a delay
            time.sleep(5)
            logger.info(f"Restarting {name}...")
            # Note: In a real implementation, we'd restart the process here
            break

        time.sleep(10)  # Check every 10 seconds

def main():
    logger.info("Starting AI Employee System (Silver Tier)...")

    # Get vault path
    vault_path = sys.argv[1] if len(sys.argv) > 1 else "."
    vault_path = Path(vault_path).resolve()
    logger.info(f"Using vault path: {vault_path}")

    # List of components to start
    components = [
        {
            'name': 'Orchestrator',
            'cmd': [sys.executable, str(vault_path / 'orchestrator.py'), str(vault_path)]
        },
        {
            'name': 'Scheduler',
            'cmd': [sys.executable, str(vault_path / 'scheduler.py'), str(vault_path)]
        }
    ]

    # Try to add watchers to components if they exist
    watcher_scripts = [
        ('Gmail Watcher', 'gmail_watcher.py'),
        ('WhatsApp Watcher', 'whatsapp_watcher.py'),
        ('LinkedIn Watcher', 'linkedin_watcher.py'),
        ('Reasoning Loop', 'reasoning_loop.py')
    ]

    for watcher_name, watcher_file in watcher_scripts:
        watcher_path = vault_path / watcher_file
        if watcher_path.exists():
            components.append({
                'name': watcher_name,
                'cmd': [sys.executable, str(watcher_path), str(vault_path)]
            })
        else:
            logger.info(f"{watcher_name} not found, skipping...")

    # Start all components
    processes = []
    threads = []

    for component in components:
        process_info = start_component(component['name'], component['cmd'])
        if process_info:
            processes.append(process_info)

            # Start a monitoring thread for each process
            monitor_thread = threading.Thread(
                target=monitor_process,
                args=(component['name'], process_info['process']),
                daemon=True
            )
            monitor_thread.start()
            threads.append(monitor_thread)

    logger.info(f"Started {len(processes)} components successfully")
    logger.info("AI Employee System is now running!")

    try:
        # Keep the main thread alive
        while True:
            # Check if any processes have died
            for i, proc_info in enumerate(processes):
                if proc_info['process'].poll() is not None:
                    logger.warning(f"{proc_info['name']} has stopped, return code: {proc_info['process'].returncode}")

                    # Try to restart
                    new_process_info = start_component(proc_info['name'], proc_info['cmd'])
                    if new_process_info:
                        processes[i] = new_process_info

                        # Start new monitoring thread
                        monitor_thread = threading.Thread(
                            target=monitor_process,
                            args=(new_process_info['name'], new_process_info['process']),
                            daemon=True
                        )
                        monitor_thread.start()
                        threads.append(monitor_thread)

            time.sleep(30)  # Check every 30 seconds

    except KeyboardInterrupt:
        logger.info("Shutting down AI Employee System...")

        # Terminate all processes
        for proc_info in processes:
            try:
                proc_info['process'].terminate()
                logger.info(f"Terminated {proc_info['name']}")
            except Exception as e:
                logger.error(f"Error terminating {proc_info['name']}: {e}")

        logger.info("AI Employee System shut down complete.")

if __name__ == "__main__":
    main()