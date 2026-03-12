"""
Facebook and Instagram Poster Agent Skills
These skills allow the AI Employee to post on Facebook and Instagram with summary generation.
"""

import requests
import json
import time
import logging
from typing import Dict, List, Optional
from pathlib import Path

class FacebookIGPosterSkill:
    """
    Agent Skill for posting on Facebook and Instagram
    """

    def __init__(self, access_token: str = None):
        self.access_token = access_token or self._get_access_token()
        self.logger = logging.getLogger(__name__)

    def _get_access_token(self) -> str:
        """
        Get access token from environment or config file
        """
        # In a real implementation, this would retrieve from secure storage
        # For now, return a placeholder
        return "PLACEHOLDER_ACCESS_TOKEN"

    def generate_post_summary(self, content: str, max_length: int = 120) -> str:
        """
        Generate a summary of the content for social media posts

        Args:
            content: Original content to summarize
            max_length: Maximum length of the summary (default 120 characters)

        Returns:
            str: Summary of the content
        """
        try:
            # Simple summary generation - in a real implementation,
            # this could use a more sophisticated summarization model
            if len(content) <= max_length:
                return content.strip()

            # Split by sentences and take the first sentence(s) that fit in the limit
            sentences = content.split('.')
            summary = ""
            for sentence in sentences:
                sentence = sentence.strip() + '.'
                if len(summary + sentence) <= max_length:
                    summary += sentence + " "
                else:
                    break

            # If the summary is still too long, just truncate
            if len(summary) > max_length:
                summary = summary[:max_length-3] + "..."

            return summary.strip()

        except Exception as e:
            self.logger.error(f"Error generating post summary: {e}")
            # Return a simple truncation as fallback
            return content[:max_length-3] + "..." if len(content) > max_length else content

    def post_to_facebook_page(self, page_id: str, content: str,
                             image_url: str = None, link: str = None) -> Dict:
        """
        Post content to a Facebook page

        Args:
            page_id: Facebook page ID
            content: Content to post
            image_url: Optional URL of image to attach
            link: Optional link to include in the post

        Returns:
            dict: Result of the operation
        """
        try:
            # Generate summary for the post
            summary = self.generate_post_summary(content)

            # Facebook Graph API endpoint
            url = f"https://graph.facebook.com/v18.0/{page_id}/feed"

            # Prepare the payload
            payload = {
                'message': summary,
                'access_token': self.access_token
            }

            # Add link if provided
            if link:
                payload['link'] = link

            # Make the API call
            response = requests.post(url, data=payload)

            if response.status_code == 200:
                result = response.json()
                post_id = result.get('id')

                self.logger.info(f"Successfully posted to Facebook page {page_id}. Post ID: {post_id}")

                return {
                    "success": True,
                    "post_id": post_id,
                    "summary": summary,
                    "message": f"Successfully posted to Facebook page {page_id}"
                }
            else:
                error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                self.logger.error(f"Error posting to Facebook: {error_msg}")

                return {
                    "success": False,
                    "error": f"Facebook API error: {error_msg}"
                }

        except Exception as e:
            self.logger.error(f"Error posting to Facebook: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def post_to_instagram_business(self, ig_user_id: str, content: str,
                                  image_url: str = None, caption_extra: str = None) -> Dict:
        """
        Post content to Instagram Business Account

        Args:
            ig_user_id: Instagram user ID
            content: Content to post
            image_url: URL of image to post
            caption_extra: Additional text to add to the caption

        Returns:
            dict: Result of the operation
        """
        try:
            # Generate summary for the post
            summary = self.generate_post_summary(content)

            # Full caption with summary and extra content
            caption = summary
            if caption_extra:
                caption += f"\n\n{caption_extra}"

            # If no image is provided, we can't post to Instagram
            if not image_url:
                return {
                    "success": False,
                    "error": "Instagram requires an image for posts"
                }

            # Step 1: Create the media object
            creation_url = f"https://graph.facebook.com/v18.0/{ig_user_id}/media"
            creation_payload = {
                'image_url': image_url,
                'caption': caption,
                'access_token': self.access_token
            }

            creation_response = requests.post(creation_url, data=creation_payload)

            if creation_response.status_code != 200:
                error_msg = creation_response.json().get('error', {}).get('message', 'Unknown error')
                self.logger.error(f"Error creating Instagram media object: {error_msg}")
                return {
                    "success": False,
                    "error": f"Instagram media creation error: {error_msg}"
                }

            # Get the media ID
            media_id = creation_response.json().get('id')

            # Step 2: Publish the media
            publish_url = f"https://graph.facebook.com/v18.0/{ig_user_id}/media_publish"
            publish_payload = {
                'creation_id': media_id,
                'access_token': self.access_token
            }

            # Wait a bit before publishing
            time.sleep(2)

            publish_response = requests.post(publish_url, data=publish_payload)

            if publish_response.status_code == 200:
                result = publish_response.json()
                post_id = result.get('id')

                self.logger.info(f"Successfully posted to Instagram. Post ID: {post_id}")

                return {
                    "success": True,
                    "post_id": post_id,
                    "summary": summary,
                    "message": f"Successfully posted to Instagram"
                }
            else:
                error_msg = publish_response.json().get('error', {}).get('message', 'Unknown error')
                self.logger.error(f"Error publishing Instagram media: {error_msg}")

                return {
                    "success": False,
                    "error": f"Instagram publish error: {error_msg}"
                }

        except Exception as e:
            self.logger.error(f"Error posting to Instagram: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def cross_post_to_both(self, content: str, image_url: str = None,
                          link: str = None, caption_extra: str = None,
                          page_id: str = None, ig_user_id: str = None) -> Dict:
        """
        Cross-post content to both Facebook and Instagram

        Args:
            content: Content to post
            image_url: Optional URL of image to attach
            link: Optional link to include in the post
            caption_extra: Additional text for Instagram caption
            page_id: Facebook page ID
            ig_user_id: Instagram user ID

        Returns:
            dict: Results for both platforms
        """
        results = {
            "facebook": None,
            "instagram": None
        }

        # Post to Facebook if page_id is provided
        if page_id:
            results["facebook"] = self.post_to_facebook_page(
                page_id, content, image_url, link
            )

        # Post to Instagram if ig_user_id and image_url is provided
        if ig_user_id and image_url:
            results["instagram"] = self.post_to_instagram_business(
                ig_user_id, content, image_url, caption_extra
            )
        elif ig_user_id and not image_url:
            results["instagram"] = {
                "success": False,
                "error": "Instagram post requires an image_url parameter"
            }

        # Overall success is True only if at least one platform succeeded
        overall_success = (
            (results["facebook"] and results["facebook"]["success"]) or
            (results["instagram"] and results["instagram"]["success"])
        )

        return {
            "success": overall_success,
            "facebook_result": results["facebook"],
            "instagram_result": results["instagram"],
            "summary": self.generate_post_summary(content)
        }


def post_to_facebook_page(content: str, page_id: str,
                         image_url: str = None, link: str = None) -> Dict:
    """
    Agent Skill function to post content to Facebook page

    Args:
        content: Content to post
        page_id: Facebook page ID
        image_url: Optional URL of image to attach
        link: Optional link to include in the post

    Returns:
        dict: Result of the operation
    """
    try:
        skill = FacebookIGPosterSkill()
        return skill.post_to_facebook_page(page_id, content, image_url, link)
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def post_to_instagram_business(content: str, ig_user_id: str,
                              image_url: str = None, caption_extra: str = None) -> Dict:
    """
    Agent Skill function to post content to Instagram business account

    Args:
        content: Content to post
        ig_user_id: Instagram user ID
        image_url: URL of image to post
        caption_extra: Additional text to add to the caption

    Returns:
        dict: Result of the operation
    """
    try:
        skill = FacebookIGPosterSkill()
        return skill.post_to_instagram_business(ig_user_id, content, image_url, caption_extra)
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def cross_post_to_facebook_and_instagram(content: str, page_id: str, ig_user_id: str,
                                       image_url: str = None, link: str = None,
                                       caption_extra: str = None) -> Dict:
    """
    Agent Skill function to cross-post content to both Facebook and Instagram

    Args:
        content: Content to post
        page_id: Facebook page ID
        ig_user_id: Instagram user ID
        image_url: Optional URL of image to attach
        link: Optional link to include in the post
        caption_extra: Additional text for Instagram caption

    Returns:
        dict: Results for both platforms
    """
    try:
        skill = FacebookIGPosterSkill()
        return skill.cross_post_to_both(
            content, image_url, link, caption_extra, page_id, ig_user_id
        )
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def generate_social_media_summary(content: str, max_length: int = 120) -> Dict:
    """
    Agent Skill function to generate a social media summary

    Args:
        content: Original content to summarize
        max_length: Maximum length of the summary

    Returns:
        dict: Generated summary
    """
    try:
        skill = FacebookIGPosterSkill()
        summary = skill.generate_post_summary(content, max_length)

        return {
            "success": True,
            "summary": summary,
            "original_length": len(content),
            "summary_length": len(summary)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# Example usage function
def suggest_social_media_content(topic: str = "business", content_type: str = "update") -> Dict:
    """
    Agent Skill function to suggest social media content based on topic

    Args:
        topic: The topic for content (e.g., "business", "technology", "industry news")
        content_type: Type of content ("update", "tip", "news", "story")

    Returns:
        dict: Suggested content ideas
    """
    try:
        suggestions = []

        if topic.lower() == "business":
            if content_type.lower() == "tip":
                suggestions = [
                    "Share a productivity tip for remote work",
                    "Post about effective team communication strategies",
                    "Offer advice on time management for entrepreneurs",
                    "Discuss the importance of work-life balance"
                ]
            elif content_type.lower() == "update":
                suggestions = [
                    "Share a company milestone or achievement",
                    "Post about a new product or service launch",
                    "Highlight a team member or company culture",
                    "Announce a new partnership or collaboration"
                ]
            else:
                suggestions = [
                    "What are your thoughts on current business trends? I'd love to hear your perspective.",
                    "Based on recent developments in business, here's my take on the industry...",
                    "Exploring the impact of current events on small businesses. What's your experience?"
                ]

        elif topic.lower() == "technology":
            if content_type.lower() == "tip":
                suggestions = [
                    "Share a technology tip for improving business efficiency",
                    "Post about cybersecurity best practices",
                    "Offer advice on using AI tools for business",
                    "Discuss the importance of data privacy"
                ]
            else:
                suggestions = [
                    "What are your thoughts on recent technology trends? I'd love to hear your perspective.",
                    "Based on recent developments in tech, here's my take on the industry...",
                    "Exploring the impact of technology on small businesses. What's your experience?"
                ]

        else:
            # General suggestions
            suggestions = [
                "Share an update about a recent company milestone.",
                "Post about industry insights or trends you're observing.",
                "Share a helpful tip or lesson learned in your field.",
                "Feature a team member or highlight company culture.",
                "Comment on a recent industry news or event."
            ]

        return {
            "success": True,
            "topic": topic,
            "content_type": content_type,
            "suggestions": suggestions[:3],  # Return first 3 suggestions
            "total_suggestions": len(suggestions)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# If run as a script for testing
if __name__ == "__main__":
    # Example usage
    print("Testing Facebook/Instagram Poster Skills...")

    # Example 1: Generate a social media summary
    content = "We're excited to announce that our company has achieved a significant milestone by completing 100+ projects this year, helping businesses transform digitally and achieve their goals through innovative solutions and dedicated service."
    summary_result = generate_social_media_summary(content)
    print("Summary Result:", summary_result)

    # Example 2: Suggest social media content
    ideas = suggest_social_media_content("business", "update")
    print("Content Ideas:", ideas)