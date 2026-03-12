# linkedin_watcher.py
import time
import logging
from pathlib import Path
from base_watcher import BaseWatcher
from datetime import datetime
import json
import requests
from playwright.sync_api import sync_playwright
import os

class LinkedInWatcher(BaseWatcher):
    def __init__(self, vault_path: str, session_path: str = None):
        super().__init__(vault_path, check_interval=300)  # Check every 5 minutes
        self.session_path = Path(session_path) if session_path else Path(vault_path) / 'linkedin_session'
        self.session_path.mkdir(exist_ok=True)
        self.browser = None
        self.page = None
        self.running = False
        # Business-related keywords to monitor
        self.keywords = ['business', 'opportunity', 'partnership', 'investment', 'sales', 'client', 'project', 'contract']

    def setup_browser(self):
        """Setup the Playwright browser instance for LinkedIn"""
        try:
            self.browser = self.playwright.chromium.launch_persistent_context(
                self.session_path,
                headless=False,  # LinkedIn requires headful mode for proper interaction
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            self.page = self.browser.new_page()
            self.page.goto('https://www.linkedin.com/feed/')
            self.logger.info("LinkedIn opened. Please log in if not already logged in.")

            # Wait for LinkedIn to load
            try:
                self.page.wait_for_selector('input[placeholder="Search"]', timeout=10000)
                self.logger.info("LinkedIn loaded successfully")
            except Exception:
                self.logger.info("Please log in to LinkedIn in the browser")
                # Wait for login
                self.page.wait_for_selector('input[placeholder="Search"]', timeout=60000)
                self.logger.info("LinkedIn logged in successfully")

        except Exception as e:
            self.logger.error(f"Error setting up LinkedIn browser: {e}")
            raise

    def check_for_updates(self) -> list:
        """Check LinkedIn for business opportunities or relevant content"""
        if not self.page:
            self.logger.error("LinkedIn page not initialized")
            return []

        try:
            opportunities = []

            # Go to relevant sections to find business opportunities
            # Check notifications page
            try:
                self.page.goto('https://www.linkedin.com/notifications/')
                time.sleep(2)

                # Look for connection requests, messages, or other notifications
                notification_elements = self.page.query_selector_all('div[tabindex="0"] span[dir="ltr"]')

                for element in notification_elements[:10]:  # Check first 10 notifications
                    text = element.inner_text().lower()
                    if any(keyword in text for keyword in self.keywords):
                        opportunity = {
                            'type': 'notification',
                            'content': text,
                            'timestamp': datetime.now().isoformat(),
                            'source': 'linkedin_notifications'
                        }
                        opportunities.append(opportunity)

            except Exception as e:
                self.logger.error(f"Error checking notifications: {e}")

            # Check feed for business content
            try:
                self.page.goto('https://www.linkedin.com/feed/')
                time.sleep(2)

                # Look for posts containing business keywords
                post_elements = self.page.query_selector_all('div.feed-shared-update-v2 article span')

                for element in post_elements[:5]:  # Check first 5 posts
                    text = element.inner_text().lower()
                    if any(keyword in text for keyword in self.keywords):
                        opportunity = {
                            'type': 'post',
                            'content': element.inner_text(),
                            'timestamp': datetime.now().isoformat(),
                            'source': 'linkedin_feed'
                        }
                        opportunities.append(opportunity)

            except Exception as e:
                self.logger.error(f"Error checking feed: {e}")

            # Check for InMail messages
            try:
                self.page.goto('https://www.linkedin.com/messaging/')
                time.sleep(2)

                # Look for new messages
                message_elements = self.page.query_selector_all('div.msg-conversation-listitem__message-snippet')

                for element in message_elements[:5]:
                    text = element.inner_text().lower()
                    if any(keyword in text for keyword in self.keywords):
                        opportunity = {
                            'type': 'message',
                            'content': element.inner_text(),
                            'timestamp': datetime.now().isoformat(),
                            'source': 'linkedin_messaging'
                        }
                        opportunities.append(opportunity)

            except Exception as e:
                self.logger.error(f"Error checking messages: {e}")

            return opportunities

        except Exception as e:
            self.logger.error(f"Error checking for LinkedIn updates: {e}")
            # Browser might have closed, try to reconnect
            try:
                self.setup_browser()
            except Exception as reconnection_error:
                self.logger.error(f"Could not reconnect: {reconnection_error}")

            return []

    def create_action_file(self, opportunity_data) -> Path:
        """Create markdown file in Needs_Action folder for LinkedIn opportunities"""
        try:
            content_type = opportunity_data['type']
            content = opportunity_data['content']
            timestamp = opportunity_data['timestamp']
            source = opportunity_data['source']

            # Determine priority based on content
            priority = 'medium'
            for keyword in self.keywords:
                if keyword in content.lower():
                    priority = 'high'
                    break

            markdown_content = f'''---
type: linkedin_opportunity
source: {source}
content_type: {content_type}
timestamp: {timestamp}
priority: {priority}
status: pending
---

## LinkedIn Opportunity
{content}

## Context
- Type: {content_type}
- Source: {source}
- Time: {timestamp}

## Suggested Actions
- [ ] Review opportunity details
- [ ] Evaluate business relevance
- [ ] Respond appropriately if it's a message
- [ ] Consider engaging with the post/connection request
- [ ] Update business development plan if relevant

## Business Development Opportunity
This LinkedIn activity may present a business opportunity or connection worth pursuing.
'''

            # Create a safe filename based on content type and timestamp
            safe_content_type = "".join(c for c in content_type if c.isalnum() or c in (' ', '-', '_')).rstrip()
            timestamp_part = timestamp.replace(":", "").replace("-", "")[:14] if timestamp else "unknown"

            filepath = self.needs_action / f'LINKEDIN_{safe_content_type}_{timestamp_part}.md'
            filepath.write_text(markdown_content)

            self.logger.info(f'Created LinkedIn opportunity file: {filepath.name}')
            return filepath
        except Exception as e:
            self.logger.error(f"Error creating LinkedIn action file: {e}")
            return None

    def run(self):
        """Main run loop for the LinkedIn watcher"""
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
                self.logger.info("LinkedIn Watcher stopped by user.")
            except Exception as e:
                self.logger.error(f"Critical error in LinkedIn Watcher: {e}")
            finally:
                if self.browser:
                    self.browser.close()

def main():
    import sys
    vault_path = sys.argv[1] if len(sys.argv) > 1 else "."
    session_path = sys.argv[2] if len(sys.argv) > 2 else None

    watcher = LinkedInWatcher(vault_path, session_path)
    watcher.run()

if __name__ == "__main__":
    main()