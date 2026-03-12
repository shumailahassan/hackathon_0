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
            self.browser = self.playwright.chromium.launch_persistent_context(
                self.session_path,
                headless=False,  # WhatsApp Web requires headful mode
                viewport={'width': 1280, 'height': 720}
            )
            self.page = self.browser.new_page()
            self.page.goto('https://web.whatsapp.com')
            self.logger.info("WhatsApp Web opened. Please scan QR code if prompted.")

            # Wait for WhatsApp Web to load
            try:
                self.page.wait_for_selector('[data-testid="chat-list"]', timeout=30000)
                self.logger.info("WhatsApp Web loaded successfully")
            except Exception:
                self.logger.info("Please scan the QR code to log in to WhatsApp Web")
                # Wait for login
                self.page.wait_for_selector('[data-testid="chat-list"]', timeout=60000)
                self.logger.info("WhatsApp Web logged in successfully")

        except Exception as e:
            self.logger.error(f"Error setting up browser: {e}")
            raise

    def check_for_updates(self) -> list:
        """Check WhatsApp Web for unread messages"""
        if not self.page:
            self.logger.error("WhatsApp page not initialized")
            return []

        try:
            messages = []

            # Get all unread chats
            unread_chats = self.page.query_selector_all('div[aria-label*="unread"]')

            for chat in unread_chats:
                try:
                    # Click on the chat to open it
                    chat.click()
                    time.sleep(1)  # Wait for messages to load

                    # Get the last few messages
                    message_elements = self.page.query_selector_all('div.copyable-text span[dir="ltr"]')

                    for msg_element in message_elements[-3:]:  # Check last 3 messages
                        message_text = msg_element.inner_text().lower()

                        # Check if message contains any of our keywords
                        if any(keyword in message_text for keyword in self.keywords):
                            # Get chat name
                            chat_name_element = self.page.query_selector('header span[data-testid="conversation-info-header-chat-title"]')
                            chat_name = chat_name_element.inner_text() if chat_name_element else "Unknown Contact"

                            message_data = {
                                'text': message_text,
                                'chat_name': chat_name,
                                'timestamp': datetime.now().isoformat()
                            }

                            messages.append(message_data)

                except Exception as e:
                    self.logger.error(f"Error processing chat: {e}")
                    continue

            return messages

        except Exception as e:
            self.logger.error(f"Error checking for WhatsApp updates: {e}")
            # Browser might have closed, try to reconnect
            try:
                self.setup_browser()
            except Exception as reconnection_error:
                self.logger.error(f"Could not reconnect: {reconnection_error}")

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

        with sync_playwright() as playwright:
            self.playwright = playwright
            try:
                self.setup_browser()
                self.running = True

                while self.running:
                    try:
                        items = self.check_for_updates()
                        for item in items:
                            self.create_action_file(item)
                    except Exception as e:
                        self.logger.error(f'Error in {self.__class__.__name__}: {e}')
                    time.sleep(self.check_interval)
            except KeyboardInterrupt:
                self.logger.info("WhatsApp Watcher stopped by user.")
            except Exception as e:
                self.logger.error(f"Critical error in WhatsApp Watcher: {e}")
            finally:
                if self.browser:
                    self.browser.close()

def main():
    import sys
    vault_path = sys.argv[1] if len(sys.argv) > 1 else "."
    session_path = sys.argv[2] if len(sys.argv) > 2 else None

    watcher = WhatsAppWatcher(vault_path, session_path)
    watcher.run()

if __name__ == "__main__":
    main()