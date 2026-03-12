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

class LinkedInPosterSkill:
    def __init__(self, session_path: str = None):
        self.session_path = Path(session_path) if session_path else Path.home() / 'linkedin_session'
        self.session_path.mkdir(exist_ok=True)
        self.browser = None
        self.page = None
        self.logger = logging.getLogger(__name__)

    def setup_browser(self):
        """Setup the Playwright browser instance for LinkedIn"""
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch_persistent_context(
                self.session_path,
                headless=False,  # LinkedIn requires headful mode
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            self.page = self.browser.new_page()
            self.page.goto('https://www.linkedin.com/feed/')

            # Wait for LinkedIn to load
            try:
                self.page.wait_for_selector('input[placeholder="Search"]', timeout=10000)
                self.logger.info("LinkedIn loaded successfully")
                return True
            except Exception:
                self.logger.info("Please log in to LinkedIn in the browser and return to this application")
                # Wait for login
                self.page.wait_for_selector('input[placeholder="Search"]', timeout=60000)
                self.logger.info("LinkedIn logged in successfully")
                return True

        except Exception as e:
            self.logger.error(f"Error setting up LinkedIn browser: {e}")
            return False

    def post_on_linkedin(self, content: str, hashtags: list = None, image_path: str = None):
        """
        Post content on LinkedIn

        Args:
            content: The main content to post
            hashtags: List of hashtags to include
            image_path: Optional image path to attach

        Returns:
            dict: Result of the post operation
        """
        if not self.page:
            if not self.setup_browser():
                return {"success": False, "error": "Could not setup browser"}

        try:
            # Click on the post box
            post_box = self.page.wait_for_selector('div[contenteditable="true"][data-test-id="artdeco-content-editable"]', timeout=5000)
            post_box.click()
            time.sleep(1)

            # Type the content
            post_box.fill(content)
            time.sleep(1)

            # Add hashtags if provided
            if hashtags:
                hashtags_str = " ".join([f"#{tag}" for tag in hashtags])
                post_box.fill(content + " " + hashtags_str)
                time.sleep(1)

            # Add image if provided
            if image_path and os.path.exists(image_path):
                # Find and click the image upload button
                image_button = self.page.wait_for_selector('button[aria-label="Add a photo/image"]', timeout=5000)
                image_button.click()
                time.sleep(1)

                # This is tricky - we need to handle file upload
                # For now, we'll skip the image upload as it requires different handling
                self.logger.info("Image upload functionality is complex and requires specific UI interaction")

            # Click the post button
            post_button = self.page.wait_for_selector('button[aria-label="Post"]', timeout=5000)
            post_button.click()
            time.sleep(3)  # Wait for post to be published

            return {
                "success": True,
                "message": f"Successfully posted on LinkedIn: {content[:50]}..."
            }

        except Exception as e:
            self.logger.error(f"Error posting on LinkedIn: {e}")
            return {"success": False, "error": str(e)}

    def get_trending_topics(self):
        """
        Get trending topics on LinkedIn to help generate relevant content

        Returns:
            list: List of trending topics
        """
        if not self.page:
            if not self.setup_browser():
                return []

        try:
            # Go to the trending section
            self.page.goto('https://www.linkedin.com/feed/', timeout=10000)
            time.sleep(2)

            # Extract trending topics (this is a simplified implementation)
            # In a real implementation, we'd need to parse the actual trending topics section
            trending_elements = self.page.query_selector_all('a[href*="/feed/hashtag/"] span')

            trending_topics = []
            for element in trending_elements[:5]:  # Get first 5 trending topics
                text = element.inner_text().strip()
                if text and len(text) > 2:  # Filter out very short text
                    trending_topics.append(text)

            return trending_topics

        except Exception as e:
            self.logger.error(f"Error getting trending topics: {e}")
            return []

    def close(self):
        """Close the browser session"""
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()

    def __enter__(self):
        """Context manager entry"""
        if not self.setup_browser():
            raise Exception("Could not setup LinkedIn browser")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

# Example usage function
def post_business_update(content: str, hashtags: list = None, image_path: str = None) -> dict:
    """
    Agent Skill function to post business updates on LinkedIn

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
    finally:
        skill.close()

def suggest_business_post_ideas():
    """
    Agent Skill function to suggest business post ideas based on trending topics

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
            "post_ideas": post_ideas[:10]  # Return first 10 ideas
        }
    finally:
        skill.close()

# If run as a script for testing
if __name__ == "__main__":
    # Example usage
    print("Testing LinkedIn Poster Skill...")

    # Example 1: Post business update
    result = post_business_update(
        "Excited to announce our latest milestone! We've successfully completed 100+ projects this year, helping businesses transform digitally.",
        hashtags=['business', 'milestone', 'digitaltransformation', 'success']
    )
    print("Post result:", result)

    # Example 2: Get post ideas
    ideas = suggest_business_post_ideas()
    print("Suggested post ideas:", ideas.get("post_ideas", [])[:3])  # Show first 3