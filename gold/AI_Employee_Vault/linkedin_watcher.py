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

# Test mode flag for development and debugging
TEST_MODE = os.getenv('TEST_MODE', 'False').lower() == 'true'

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
            self.logger.info("Browser launch - Initializing LinkedIn session...")
            self.logger.info(f"Session path: {self.session_path}")
            self.browser = self.playwright.chromium.launch_persistent_context(
                self.session_path,
                headless=False,  # LinkedIn requires headful mode for proper interaction
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            self.page = self.browser.new_page()
            self.logger.info(f"Browser initialized, opening LinkedIn at https://www.linkedin.com/feed/...")

            # Go to LinkedIn and wait for it to load
            self.logger.info("Navigating to LinkedIn feed...")
            self.page.goto('https://www.linkedin.com/feed/', timeout=60000)  # Increased timeout
            self.logger.info("LinkedIn page loaded, waiting for full page load...")

            # Wait for the page to fully load before checking login
            self.page.wait_for_timeout(5000)  # Increased wait time for full load

            # Wait for LinkedIn to load properly and check if user is logged in
            self.logger.info("Checking login status...")
            login_detected = self.wait_for_login_state()

            if login_detected:
                self.logger.info("LinkedIn session is active and logged in successfully")
            else:
                self.logger.info("LinkedIn session not logged in. Please log in in the browser...")
                # Wait for login with extended timeout
                login_detected = self.wait_for_login_state(timeout=120000)
                if login_detected:
                    self.logger.info("LinkedIn logged in successfully")
                    # Additional wait after login to ensure session is properly saved
                    self.page.wait_for_timeout(3000)
                    self.logger.info("Session save confirmation complete")
                else:
                    self.logger.warning("Could not detect login. Make sure you're properly logged in.")

        except Exception as e:
            self.logger.error(f"Error setting up LinkedIn browser: {e}")
            if TEST_MODE:
                self.logger.info(f"[TEST MODE] Error details: {type(e).__name__}: {str(e)}")
            raise

    def ensure_browser_connected(self):
        """Ensure the browser is still connected and working"""
        try:
            if not self.browser or not self.page:
                self.logger.warning("Browser or page not initialized, attempting to setup browser...")
                self.setup_browser()
                return True
            # Check if we can interact with the page
            self.page.title()  # This will throw an exception if the page is closed
            return True
        except Exception as e:
            self.logger.warning(f"Browser connection lost: {e}, reconnecting...")
            try:
                self.setup_browser()
                return True
            except Exception as reconnection_error:
                self.logger.error(f"Could not reconnect browser: {reconnection_error}")
                return False

    def wait_for_login_state(self, timeout=10000):
        """Wait for login state to be detected by checking multiple indicators"""
        try:
            self.logger.info("Starting login detection...")

            # Wait a bit for the page to fully load before checking for login elements
            self.page.wait_for_timeout(2000)

            # Wait extra time to ensure page is not still loading
            try:
                self.page.wait_for_load_state('networkidle', timeout=5000)
                self.logger.info("Page has reached network idle state")
            except:
                self.logger.info("Page didn't reach network idle, continuing with checks...")

            # Check for multiple login indicators - any of these mean the user is logged in
            # 1. Check for feed URL (most reliable indicator)
            try:
                current_url = self.page.url
                self.logger.info(f"Current URL: {current_url}")
                if 'linkedin.com/feed' in current_url:
                    self.logger.info("Login detected via feed URL")
                    return True
            except Exception as e:
                self.logger.debug(f"URL check failed: {e}")
                pass

            # 2. Check for profile avatar (most reliable visual indicator)
            try:
                # Wait for profile element that appears after login
                self.page.wait_for_selector('img[alt*="Photo"]', timeout=timeout//4)
                self.logger.info("Login detected via profile avatar")
                return True
            except:
                pass

            # 3. Check for profile dropdown element
            try:
                self.page.wait_for_selector('div.global-nav__me', timeout=timeout//4)
                self.logger.info("Login detected via profile navigation")
                return True
            except:
                pass

            # 4. Check for search input (appears after login)
            try:
                self.page.wait_for_selector('input[placeholder="Search"]', timeout=timeout//4)
                self.logger.info("Login detected via search input")
                return True
            except:
                pass

            # 5. Check for navigation elements that appear after login
            try:
                self.page.wait_for_selector('a[href="/feed/"]', timeout=timeout//4)
                self.logger.info("Login detected via feed navigation")
                return True
            except:
                pass

            # 6. Check for notification icon (appears after login)
            try:
                self.page.wait_for_selector('[data-test-global-typeahead-search]', timeout=timeout//4)
                self.logger.info("Login detected via global search")
                return True
            except:
                pass

            # 7. Check for jobs, messaging, network elements that appear after login
            try:
                self.page.wait_for_selector('a[href="/jobs/"]', timeout=timeout//4)
                self.logger.info("Login detected via jobs navigation")
                return True
            except:
                pass

            self.logger.debug("No login indicators found")
            return False
        except Exception as e:
            self.logger.warning(f"Error during login detection: {e}")
            return False

    def check_for_updates(self) -> list:
        """Check LinkedIn for business opportunities or relevant content"""
        # Ensure browser is connected before proceeding
        if not self.ensure_browser_connected():
            self.logger.error("Could not establish browser connection")
            return []

        opportunities = []

        try:
            # Check notifications page
            try:
                self.logger.info("Navigating to LinkedIn notifications...")
                self.page.goto('https://www.linkedin.com/notifications/', timeout=20000)
                time.sleep(2)

                # Wait for notifications to load
                try:
                    self.page.wait_for_selector('div[tabindex="0"] span[dir="ltr"], .notification-card', timeout=10000)
                except:
                    self.logger.info("No notifications found or notifications not loaded")

                # Look for connection requests, messages, or other notifications
                notification_elements = self.page.query_selector_all('div[tabindex="0"] span[dir="ltr"]')
                self.logger.info(f"Found {len(notification_elements)} notification elements")

                for element in notification_elements[:10]:  # Check first 10 notifications
                    try:
                        text = element.inner_text().lower()
                        if text and any(keyword in text for keyword in self.keywords):
                            opportunity = {
                                'type': 'notification',
                                'content': element.inner_text(),
                                'timestamp': datetime.now().isoformat(),
                                'source': 'linkedin_notifications'
                            }
                            opportunities.append(opportunity)
                            if TEST_MODE:
                                self.logger.info(f"[TEST MODE] Found notification opportunity: {element.inner_text()[:100]}...")
                    except Exception as element_error:
                        self.logger.warning(f"Error processing notification element: {element_error}")
                        continue

            except Exception as e:
                self.logger.error(f"Error checking notifications: {e}")
                if TEST_MODE:
                    self.logger.info(f"[TEST MODE] Notification error details: {type(e).__name__}: {str(e)}")

            # Check feed for business content
            try:
                self.logger.info("Navigating to LinkedIn feed...")
                self.page.goto('https://www.linkedin.com/feed/', timeout=20000)
                time.sleep(2)

                # Wait for feed to load
                try:
                    self.page.wait_for_selector('div.feed-shared-update-v2, .feed-shared-text, [data-id]', timeout=10000)
                except:
                    self.logger.info("Feed not loaded or no posts found")

                # Look for posts containing business keywords
                post_elements = self.page.query_selector_all('div.feed-shared-update-v2 article span, .feed-shared-text__link')
                self.logger.info(f"Found {len(post_elements)} post elements")

                for element in post_elements[:5]:  # Check first 5 posts
                    try:
                        inner_text = element.inner_text()
                        if inner_text:
                            text = inner_text.lower()
                            if any(keyword in text for keyword in self.keywords):
                                opportunity = {
                                    'type': 'post',
                                    'content': element.inner_text(),
                                    'timestamp': datetime.now().isoformat(),
                                    'source': 'linkedin_feed'
                                }
                                opportunities.append(opportunity)
                                if TEST_MODE:
                                    self.logger.info(f"[TEST MODE] Found post opportunity: {element.inner_text()[:100]}...")
                    except Exception as element_error:
                        self.logger.warning(f"Error processing post element: {element_error}")
                        continue

            except Exception as e:
                self.logger.error(f"Error checking feed: {e}")
                if TEST_MODE:
                    self.logger.info(f"[TEST MODE] Feed error details: {type(e).__name__}: {str(e)}")

            # Check for InMail messages
            try:
                self.logger.info("Navigating to LinkedIn messaging...")
                self.page.goto('https://www.linkedin.com/messaging/', timeout=20000)
                time.sleep(2)

                # Wait for messaging to load
                try:
                    self.page.wait_for_selector('div.msg-conversation-listitem__message-snippet, .msg-thread-title', timeout=10000)
                except:
                    self.logger.info("Messaging not loaded or no messages found")

                # Look for new messages
                message_elements = self.page.query_selector_all('div.msg-conversation-listitem__message-snippet')
                self.logger.info(f"Found {len(message_elements)} message elements")

                for element in message_elements[:5]:
                    try:
                        inner_text = element.inner_text()
                        if inner_text:
                            text = inner_text.lower()
                            if any(keyword in text for keyword in self.keywords):
                                opportunity = {
                                    'type': 'message',
                                    'content': element.inner_text(),
                                    'timestamp': datetime.now().isoformat(),
                                    'source': 'linkedin_messaging'
                                }
                                opportunities.append(opportunity)
                                if TEST_MODE:
                                    self.logger.info(f"[TEST MODE] Found message opportunity: {element.inner_text()[:100]}...")
                    except Exception as element_error:
                        self.logger.warning(f"Error processing message element: {element_error}")
                        continue

            except Exception as e:
                self.logger.error(f"Error checking messages: {e}")
                if TEST_MODE:
                    self.logger.info(f"[TEST MODE] Message error details: {type(e).__name__}: {str(e)}")

            return opportunities

        except Exception as e:
            self.logger.error(f"Error checking for LinkedIn updates: {e}")
            if TEST_MODE:
                self.logger.info(f"[TEST MODE] General error details: {type(e).__name__}: {str(e)}")

            # Browser might have closed, try to reconnect
            try:
                self.setup_browser()
            except Exception as reconnection_error:
                self.logger.error(f"Could not reconnect: {reconnection_error}")
                if TEST_MODE:
                    self.logger.info(f"[TEST MODE] Reconnection error details: {type(reconnection_error).__name__}: {str(reconnection_error)}")

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
                            self.logger.info(f"[TEST MODE] LinkedIn check #{run_count}")

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
                                    self.ensure_browser_connected()
                                else:
                                    self.logger.error(f"Failed to check LinkedIn updates after {max_retries} attempts: {check_error}")
                                    if TEST_MODE:
                                        self.logger.info(f"[TEST MODE] Check updates error details: {type(check_error).__name__}: {str(check_error)}")

                        if TEST_MODE:
                            self.logger.info(f"[TEST MODE] Found {len(items)} LinkedIn opportunities")

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
                self.logger.info("LinkedIn Watcher stopped by user.")
            except Exception as e:
                self.logger.error(f"Critical error in LinkedIn Watcher: {e}")
                if TEST_MODE:
                    self.logger.info(f"[TEST MODE] Critical error details: {type(e).__name__}: {str(e)}")
            finally:
                if self.browser:
                    self.browser.close()
                    self.logger.info("LinkedIn browser closed")

def main():
    import sys
    vault_path = sys.argv[1] if len(sys.argv) > 1 else "."
    session_path = sys.argv[2] if len(sys.argv) > 2 else None

    watcher = LinkedInWatcher(vault_path, session_path)
    watcher.run()

if __name__ == "__main__":
    main()