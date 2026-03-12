# whatsapp_watcher.py
import time
import logging
from pathlib import Path
from base_watcher import BaseWatcher
from datetime import datetime
import json
from playwright.sync_api import sync_playwright
import os
import threading

# Test mode flag for development and debugging
TEST_MODE = os.getenv('TEST_MODE', 'False').lower() == 'true'

class WhatsAppWatcher(BaseWatcher):
    def __init__(self, vault_path: str, session_path: str = None):
        super().__init__(vault_path, check_interval=30)  # Check every 30 seconds
        self.session_path = Path(session_path) if session_path else Path(vault_path) / 'whatsapp_session'
        self.session_path.mkdir(exist_ok=True)
        self.keywords = ['urgent', 'asap', 'invoice', 'payment', 'help', 'important', 'needed', 'require']
        self.browser = None
        self.page = None
        self.running = False

    def setup_browser(self):
        """Setup the Playwright browser instance"""
        try:
            self.logger.info("Browser launch - Initializing WhatsApp session...")
            self.logger.info(f"Session path: {self.session_path}")
            self.browser = self.playwright.chromium.launch_persistent_context(
                self.session_path,
                headless=False,  # WhatsApp Web requires headful mode
                viewport={'width': 1280, 'height': 720}
            )
            self.page = self.browser.new_page()
            self.logger.info("Browser initialized, opening WhatsApp Web...")
            self.page.goto('https://web.whatsapp.com')

            # Wait for WhatsApp Web to load properly and check if user is logged in
            self.logger.info("Page loaded, waiting for content to load...")
            self.page.wait_for_timeout(5000)

            try:
                self.page.wait_for_load_state('networkidle', timeout=10000)
            except:
                self.logger.info("Page didn't reach network idle, proceeding with checks...")

            self.logger.info("Checking WhatsApp login status...")
            login_detected = self.wait_for_login_state()

            if login_detected:
                self.logger.info("WhatsApp Web session is active and logged in successfully")
                self.logger.info("Session save confirmation complete")
            else:
                self.logger.info("WhatsApp Web not logged in. Please scan QR code in the browser...")
                # Wait for login with extended timeout
                login_detected = self.wait_for_login_state(timeout=120000)
                if login_detected:
                    self.logger.info("WhatsApp Web logged in successfully")
                    self.page.wait_for_timeout(3000)
                    self.logger.info("Session save confirmation complete")
                else:
                    self.logger.warning("Could not detect WhatsApp login. Make sure you're properly logged in.")

        except Exception as e:
            self.logger.error(f"Error setting up browser: {e}")
            if TEST_MODE:
                self.logger.info(f"[TEST MODE] Error details: {type(e).__name__}: {str(e)}")
            raise

    def wait_for_login_state(self, timeout=30000):
        """Wait for login state to be detected by checking multiple indicators"""
        try:
            self.logger.info("Starting WhatsApp login detection...")

            # Wait a bit for the page to fully load before checking for login elements
            self.page.wait_for_timeout(3000)  # Increased wait time for full page load

            # Wait extra time to ensure page is not still loading
            try:
                self.page.wait_for_load_state('networkidle', timeout=5000)
                self.logger.info("Page has reached network idle state")
            except:
                self.logger.info("Page didn't reach network idle, continuing with checks...")

            # Check for multiple login indicators - any of these mean the user is logged in
            # 1. Check if QR code is present (which means NOT logged in)
            try:
                # If QR code is visible, user is not logged in yet
                qr_selectors = ['[data-ref]', 'div[data-ref]', '#qrcode', 'canvas']
                for qr_selector in qr_selectors:
                    try:
                        qr_present = self.page.query_selector(qr_selector)
                        if qr_present:
                            # Double-check by checking if it's visible
                            if qr_present.is_visible():
                                self.logger.info(f"QR code detected with selector '{qr_selector}' - user not logged in yet")
                                return False
                    except:
                        continue  # Try next selector
            except Exception as qr_error:
                self.logger.debug(f"QR code detection failed: {qr_error}")
                pass  # If we can't detect QR, proceed with other checks

            # 2. Check for main chat list (original selector)
            try:
                self.logger.debug("Checking for chat list...")
                self.page.wait_for_selector('[data-testid="chat-list"]', timeout=timeout//4)
                self.logger.info("Login detected via chat list")
                return True
            except:
                pass

            # 3. Check for chat list container (alternative selector)
            try:
                self.logger.debug("Checking for chat list container...")
                self.page.wait_for_selector('div[aria-label="Chat list"]', timeout=timeout//4)
                self.logger.info("Login detected via chat list container")
                return True
            except:
                pass

            # 4. Check for main app container that appears after login
            try:
                self.logger.debug("Checking for main app container...")
                self.page.wait_for_selector('div#pane-side', timeout=timeout//4)
                self.logger.info("Login detected via pane-side")
                return True
            except:
                pass

            # 5. Check for user profile/avatar area (highly reliable indicator)
            try:
                self.logger.debug("Checking for user profile...")
                self.page.wait_for_selector('[data-testid="chat-list"] [role="gridcell"] img', timeout=timeout//4)
                self.logger.info("Login detected via user profile image")
                return True
            except:
                pass

            # 6. Check for status indicators that appear after login
            try:
                self.logger.debug("Checking for status indicators...")
                self.page.wait_for_selector('[data-testid="default-user"]', timeout=timeout//4)
                self.logger.info("Login detected via user status")
                return True
            except:
                pass

            # 7. Check for the main app area that appears only after login
            try:
                self.logger.debug("Checking for main app area...")
                self.page.wait_for_selector('div[role="tablist"]', timeout=timeout//4)
                self.logger.info("Login detected via main app area")
                return True
            except:
                pass

            self.logger.debug("No login indicators found")
            return False
        except Exception as e:
            self.logger.warning(f"Error during WhatsApp login detection: {e}")
            return False

    def check_for_updates(self) -> list:
        """Check WhatsApp Web for unread messages"""
        # Ensure browser is connected before proceeding
        try:
            if not self.page or not self.browser:
                self.logger.error("WhatsApp page or browser not initialized")
                self.setup_browser()
        except Exception as e:
            self.logger.error(f"Could not initialize WhatsApp browser: {e}")
            return []

        messages = []

        try:
            # Ensure page is accessible
            try:
                self.page.title()  # This will throw an exception if the page is closed
            except Exception:
                self.logger.warning("WhatsApp page seems disconnected, reconnecting...")
                self.setup_browser()
                if not self.page:
                    self.logger.error("Could not reinitialize WhatsApp page")
                    return messages

            # Get all unread chats
            try:
                unread_chats = self.page.query_selector_all('div[aria-label*="unread"]')
            except Exception as e:
                self.logger.warning(f"Could not get unread chats: {e}")
                unread_chats = []

            self.logger.info(f"Found {len(unread_chats)} unread chats")

            for chat in unread_chats:
                try:
                    # Click on the chat to open it
                    chat.click()
                    time.sleep(1)  # Wait for messages to load

                    # Get the last few messages
                    try:
                        message_elements = self.page.query_selector_all('div.copyable-text span[dir="ltr"]')
                    except Exception as e:
                        self.logger.warning(f"Could not get message elements: {e}")
                        continue

                    for msg_element in message_elements[-3:]:  # Check last 3 messages
                        try:
                            message_text = msg_element.inner_text().lower()
                            if not message_text.strip():
                                continue  # Skip empty messages

                            # Check if message contains any of our keywords
                            if any(keyword in message_text for keyword in self.keywords):
                                # Get chat name
                                try:
                                    chat_name_element = self.page.query_selector('header span[data-testid="conversation-info-header-chat-title"]')
                                    chat_name = chat_name_element.inner_text() if chat_name_element else "Unknown Contact"
                                except:
                                    chat_name = "Unknown Contact"

                                message_data = {
                                    'text': message_text,
                                    'chat_name': chat_name,
                                    'timestamp': datetime.now().isoformat()
                                }

                                messages.append(message_data)
                        except Exception as msg_error:
                            self.logger.warning(f"Error processing message: {msg_error}")
                            continue

                except Exception as e:
                    self.logger.error(f"Error processing chat: {e}")
                    continue

            # Also check for new messages without unread indicators
            try:
                # Navigate to main chats page
                self.page.goto('https://web.whatsapp.com', timeout=10000)
                time.sleep(2)

                # Get all chat elements
                all_chats = self.page.query_selector_all('div[role="row"]')

                for chat_element in all_chats[:5]:  # Check first 5 chats
                    try:
                        # Click on chat
                        chat_element.click()
                        time.sleep(1)

                        # Check recent messages
                        recent_messages = self.page.query_selector_all('div.copyable-text span[dir="ltr"]')

                        for msg_element in recent_messages[-2:]:  # Check last 2 messages
                            message_text = msg_element.inner_text().lower()

                            if any(keyword in message_text for keyword in self.keywords):
                                # Get chat name
                                try:
                                    chat_name_element = self.page.query_selector('header span[data-testid="conversation-info-header-chat-title"]')
                                    chat_name = chat_name_element.inner_text() if chat_name_element else "Unknown Contact"
                                except:
                                    chat_name = "Unknown Contact"

                                message_data = {
                                    'text': message_text,
                                    'chat_name': chat_name,
                                    'timestamp': datetime.now().isoformat()
                                }

                                # Avoid duplicates
                                if message_data not in messages:
                                    messages.append(message_data)
                    except Exception as chat_check_error:
                        self.logger.debug(f"Could not check chat: {chat_check_error}")
                        continue
            except Exception as e:
                self.logger.debug(f"Could not check all chats: {e}")

            return messages

        except Exception as e:
            self.logger.error(f"Error checking for WhatsApp updates: {e}")
            if TEST_MODE:
                self.logger.info(f"[TEST MODE] WhatsApp check error details: {type(e).__name__}: {str(e)}")

            # Browser might have closed, try to reconnect
            try:
                self.setup_browser()
            except Exception as reconnection_error:
                self.logger.error(f"Could not reconnect: {reconnection_error}")
                if TEST_MODE:
                    self.logger.info(f"[TEST MODE] Reconnection error details: {type(reconnection_error).__name__}: {str(reconnection_error)}")

            return []

    def create_action_file(self, message_data) -> Path:
        """Create markdown file in Needs_Action folder for the WhatsApp message"""
        try:
            text = message_data['text']
            chat_name = message_data['chat_name']
            timestamp = message_data['timestamp']

            # Determine priority based on keywords
            priority = 'medium'
            for keyword in self.keywords:
                if keyword in text:
                    priority = 'high'
                    break

            content = f'''---
type: whatsapp_message
from: {chat_name}
timestamp: {timestamp}
priority: {priority}
status: pending
---

## WhatsApp Message
{message_data['text']}

## Context
- Contact: {chat_name}
- Time: {timestamp}

## Suggested Actions
- [ ] Review message content
- [ ] Respond appropriately
- [ ] Create business task if needed
- [ ] Mark as resolved after action

## Business Trigger
This message contains business-relevant keywords and may require immediate action.
'''

            # Sanitize filename
            safe_chat_name = "".join(c for c in chat_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            if len(safe_chat_name) > 30:
                safe_chat_name = safe_chat_name[:30]

            filepath = self.needs_action / f'WHATSAPP_{safe_chat_name}_{len(str(timestamp)) > 0 and timestamp.replace(":", "").replace("-", "")[:14] or "unknown"}.md'
            filepath.write_text(content)

            self.logger.info(f'Created WhatsApp action file: {filepath.name}')
            return filepath
        except Exception as e:
            self.logger.error(f"Error creating WhatsApp action file: {e}")
            return None

    def run(self):
        """Main run loop for the watcher with playwright context management"""
        self.logger.info(f'Starting {self.__class__.__name__}')

        run_count = 0
        max_runs = 1 if TEST_MODE else float('inf')  # Run only once in test mode

        with sync_playwright() as playwright:
            self.playwright = playwright
            try:
                self.setup_browser()
                self.running = True

                while self.running and run_count < max_runs:
                    run_count += 1
                    try:
                        if TEST_MODE:
                            self.logger.info(f"[TEST MODE] WhatsApp check #{run_count}")

                        # Add retry logic for the check operation
                        retry_count = 0
                        max_retries = 3
                        items = []
                        while retry_count < max_retries:
                            try:
                                items = self.check_for_updates()
                                break  # Success, exit retry loop
                            except Exception as check_error:
                                retry_count += 1
                                self.logger.warning(f"Attempt {retry_count} failed: {check_error}")
                                if retry_count < max_retries:
                                    time.sleep(5)  # Wait before retry
                                    # Ensure browser is still connected
                                    if not self.page or not self.browser:
                                        self.setup_browser()
                                else:
                                    self.logger.error(f"Failed to check WhatsApp updates after {max_retries} attempts: {check_error}")
                                    if TEST_MODE:
                                        self.logger.info(f"[TEST MODE] Check updates error details: {type(check_error).__name__}: {str(check_error)}")

                        if TEST_MODE:
                            self.logger.info(f"[TEST MODE] Found {len(items)} WhatsApp messages")

                        for item in items:
                            self.create_action_file(item)
                    except Exception as e:
                        self.logger.error(f'Error in {self.__class__.__name__}: {e}')
                        if TEST_MODE:
                            self.logger.info(f"[TEST MODE] Error details: {type(e).__name__}: {str(e)}")

                    # Exit after one cycle in test mode
                    if TEST_MODE:
                        break

                    time.sleep(self.check_interval)

            except KeyboardInterrupt:
                self.logger.info("WhatsApp Watcher stopped by user.")
            except Exception as e:
                self.logger.error(f"Critical error in WhatsApp Watcher: {e}")
                if TEST_MODE:
                    self.logger.info(f"[TEST MODE] Critical error details: {type(e).__name__}: {str(e)}")
            finally:
                if self.browser:
                    self.browser.close()
                    self.logger.info("WhatsApp browser closed")

def main():
    import sys
    vault_path = sys.argv[1] if len(sys.argv) > 1 else "."
    session_path = sys.argv[2] if len(sys.argv) > 2 else None

    watcher = WhatsAppWatcher(vault_path, session_path)
    watcher.run()

if __name__ == "__main__":
    main()