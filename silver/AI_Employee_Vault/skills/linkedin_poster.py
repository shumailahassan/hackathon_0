"""
LinkedIn Poster Agent Skill
This skill allows the AI Employee to automatically post on LinkedIn for business promotion.
"""
import os
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
import logging
import asyncio
from typing import Dict, List, Optional, Any


class LinkedInPosterSkill:
    """
    Modular LinkedIn poster skill with enhanced error handling and logging.
    """

    def __init__(self, session_path: str = None, headless: bool = False):
        """
        Initialize the LinkedIn poster skill.

        Args:
            session_path: Path to store browser session data
            headless: Whether to run browser in headless mode (LinkedIn may require headful)
        """
        self.session_path = Path(session_path) if session_path else Path.home() / 'linkedin_session'
        self.session_path.mkdir(exist_ok=True)
        self.browser = None
        self.page = None
        self.playwright = None
        self.headless = headless  # LinkedIn usually requires headful mode
        self.logger = logging.getLogger(__name__)
        self._setup_logger()

    def _setup_logger(self):
        """Setup modular logging configuration."""
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        # Only add handler if not already added
        if not self.logger.handlers:
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def setup_browser(self) -> bool:
        """
        Setup the Playwright browser instance for LinkedIn with error handling.

        Returns:
            bool: True if setup successful, False otherwise
        """
        try:
            if self.playwright is None:
                self.playwright = sync_playwright().start()

            self.browser = self.playwright.chromium.launch_persistent_context(
                self.session_path,
                headless=self.headless,  # LinkedIn usually requires headful mode
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )

            self.page = self.browser.new_page()
            self.logger.info("Navigating to LinkedIn...")
            self.page.goto('https://www.linkedin.com/feed/')

            # Wait for LinkedIn to load
            try:
                self.page.wait_for_selector('input[placeholder="Search"]', timeout=10000)
                self.logger.info("LinkedIn loaded successfully")
                return True
            except Exception:
                self.logger.warning("LinkedIn may require manual login. Please log in in the browser.")
                # Wait for login
                self.page.wait_for_selector('input[placeholder="Search"]', timeout=60000)
                self.logger.info("LinkedIn login completed successfully")
                return True

        except Exception as e:
            self.logger.error(f"Error setting up LinkedIn browser: {e}", exc_info=True)
            return False

    def post_on_linkedin(self, content: str, hashtags: List[str] = None,
                        image_path: str = None) -> Dict[str, Any]:
        """
        Post content on LinkedIn with enhanced error handling.

        Args:
            content: The main content to post
            hashtags: List of hashtags to include
            image_path: Optional image path to attach

        Returns:
            dict: Result of the post operation
        """
        try:
            if not self.page:
                if not self.setup_browser():
                    return {"success": False, "error": "Could not setup browser"}

            # Validate inputs
            if not content or not content.strip():
                return {"success": False, "error": "Content cannot be empty"}

            # Click on the post box
            self.logger.info("Attempting to find and click the post box...")
            post_box = self.page.wait_for_selector(
                'div[contenteditable="true"][data-test-id="artdeco-content-editable"]',
                timeout=10000
            )
            post_box.click()
            time.sleep(1)

            # Type the content
            self.logger.info("Typing content...")
            post_box.fill(content)
            time.sleep(1)

            # Add hashtags if provided
            if hashtags and isinstance(hashtags, list):
                hashtags_str = " ".join([f"#{tag.strip()}" for tag in hashtags if tag.strip()])
                if hashtags_str:
                    post_box.fill(content + " " + hashtags_str)
                    time.sleep(1)

            # Add image if provided
            if image_path and os.path.exists(image_path):
                try:
                    # Find and click the image upload button
                    image_button = self.page.wait_for_selector(
                        'button[aria-label="Add a photo/image"]',
                        timeout=5000
                    )
                    image_button.click()
                    time.sleep(2)

                    # Handle file upload - use set_input_files for reliability
                    file_chooser = self.page.wait_for_event("filechooser")
                    file_chooser.set_files(image_path)
                    time.sleep(3)  # Wait for image to upload
                    self.logger.info(f"Image uploaded: {image_path}")
                except Exception as e:
                    self.logger.warning(f"Could not upload image {image_path}: {e}")

            # Click the post button
            self.logger.info("Attempting to post...")
            post_button = self.page.wait_for_selector(
                'button[aria-label="Post"]',
                timeout=10000
            )
            post_button.click()
            time.sleep(5)  # Wait for post to be published

            self.logger.info("Successfully posted on LinkedIn")
            return {
                "success": True,
                "message": f"Successfully posted on LinkedIn: {content[:50]}...",
                "content_length": len(content)
            }

        except Exception as e:
            self.logger.error(f"Error posting on LinkedIn: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def get_trending_topics(self) -> List[str]:
        """
        Get trending topics on LinkedIn to help generate relevant content.

        Returns:
            list: List of trending topics
        """
        try:
            if not self.page:
                if not self.setup_browser():
                    self.logger.error("Could not setup browser to get trending topics")
                    return []

            # Go to the trending section
            self.logger.info("Fetching trending topics...")
            self.page.goto('https://www.linkedin.com/feed/', timeout=10000)
            time.sleep(2)

            # Extract trending topics (this is a simplified implementation)
            # In a real implementation, we'd need to parse the actual trending topics section
            trending_elements = self.page.query_selector_all('a[href*="/feed/hashtag/"] span')

            trending_topics = []
            for element in trending_elements[:10]:  # Get first 10 trending topics
                text = element.inner_text().strip()
                if text and len(text) > 2:  # Filter out very short text
                    trending_topics.append(text)

            self.logger.info(f"Found {len(trending_topics)} trending topics")
            return trending_topics

        except Exception as e:
            self.logger.error(f"Error getting trending topics: {e}", exc_info=True)
            return []

    def get_network_updates(self) -> List[Dict[str, str]]:
        """
        Get recent network updates (connections, messages, etc.) from LinkedIn.

        Returns:
            list: List of network updates
        """
        updates = []
        try:
            if not self.page:
                if not self.setup_browser():
                    self.logger.error("Could not setup browser to get network updates")
                    return updates

            # Check notifications
            self.page.goto('https://www.linkedin.com/notifications/', timeout=10000)
            time.sleep(2)

            # Look for notification elements
            notification_elements = self.page.query_selector_all('div[tabindex="0"] span[dir="ltr"]')

            for element in notification_elements[:5]:  # Check first 5 notifications
                text = element.inner_text().strip()
                if text:
                    updates.append({
                        "type": "notification",
                        "content": text,
                        "timestamp": time.time()
                    })

            self.logger.info(f"Found {len(updates)} network updates")
            return updates

        except Exception as e:
            self.logger.error(f"Error getting network updates: {e}", exc_info=True)
            return updates

    def close(self):
        """Close the browser session with error handling."""
        try:
            if self.browser:
                self.browser.close()
                self.logger.info("Browser session closed")
        except Exception as e:
            self.logger.error(f"Error closing browser: {e}")

        try:
            if self.playwright:
                self.playwright.stop()
                self.logger.info("Playwright stopped")
        except Exception as e:
            self.logger.error(f"Error stopping playwright: {e}")

    def __enter__(self):
        """Context manager entry."""
        if not self.setup_browser():
            self.logger.error("Could not setup LinkedIn browser in context manager")
            raise Exception("Could not setup LinkedIn browser")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


class LinkedInPosterModule:
    """
    Module wrapper for LinkedIn posting functionality with enhanced modularity.
    """

    @staticmethod
    def post_business_update(content: str, hashtags: List[str] = None,
                           image_path: str = None) -> Dict[str, Any]:
        """
        Agent Skill function to post business updates on LinkedIn.

        Args:
            content: The business update content to post
            hashtags: List of relevant hashtags (e.g., ['business', 'startup', 'innovation'])
            image_path: Optional path to an image to attach

        Returns:
            dict: Result of the posting operation
        """
        skill = LinkedInPosterSkill()
        try:
            result = skill.post_on_linkedin(content, hashtags, image_path)
            return result
        except Exception as e:
            logging.error(f"Error in post_business_update: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
        finally:
            skill.close()

    @staticmethod
    def suggest_business_post_ideas() -> Dict[str, Any]:
        """
        Agent Skill function to suggest business post ideas based on trending topics.

        Returns:
            dict: List of post ideas
        """
        skill = LinkedInPosterSkill()
        try:
            trending = skill.get_trending_topics()

            # Generate post ideas based on trending topics
            post_ideas = []

            if trending:
                for topic in trending[:3]:
                    ideas = [
                        f"What are your thoughts on {topic}? I'd love to hear your perspective on this trending topic.",
                        f"Based on the trending topic #{topic}, here's my take on how it's affecting our industry...",
                        f"Exploring the impact of {topic} on small businesses. What's your experience?"
                    ]
                    post_ideas.extend(ideas)

            # Add some general business post ideas
            general_ideas = [
                "Share an update about a recent company milestone or achievement.",
                "Post about industry insights or trends you're observing.",
                "Share a helpful tip or lesson learned in business.",
                "Feature a team member or highlight company culture.",
                "Comment on a recent industry news or event."
            ]

            post_ideas.extend(general_ideas)

            return {
                "success": True,
                "trending_topics": trending,
                "post_ideas": post_ideas[:10],  # Return first 10 ideas
                "timestamp": time.time()
            }
        except Exception as e:
            logging.error(f"Error in suggest_business_post_ideas: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
        finally:
            skill.close()

    @staticmethod
    def get_linkedin_updates() -> Dict[str, Any]:
        """
        Get recent LinkedIn network updates.

        Returns:
            dict: Network updates and metadata
        """
        skill = LinkedInPosterSkill()
        try:
            updates = skill.get_network_updates()
            return {
                "success": True,
                "updates": updates,
                "count": len(updates),
                "timestamp": time.time()
            }
        except Exception as e:
            logging.error(f"Error in get_linkedin_updates: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
        finally:
            skill.close()


# Convenience functions for backward compatibility
def post_business_update(content: str, hashtags: List[str] = None,
                        image_path: str = None) -> Dict[str, Any]:
    """
    Backward-compatible function for posting business updates.
    """
    return LinkedInPosterModule.post_business_update(content, hashtags, image_path)

def suggest_business_post_ideas() -> Dict[str, Any]:
    """
    Backward-compatible function for suggesting post ideas.
    """
    return LinkedInPosterModule.suggest_business_post_ideas()


# If run as a script for testing
if __name__ == "__main__":
    # Example usage
    print("Testing LinkedIn Poster Skill...")

    # Example 1: Post business update
    result = LinkedInPosterModule.post_business_update(
        "Excited to announce our latest milestone! We've successfully completed 100+ projects this year, helping businesses transform digitally.",
        hashtags=['business', 'milestone', 'digitaltransformation', 'success']
    )
    print("Post result:", result)

    # Example 2: Get post ideas
    ideas = LinkedInPosterModule.suggest_business_post_ideas()
    print("Suggested post ideas:", ideas.get("post_ideas", [])[:3])  # Show first 3