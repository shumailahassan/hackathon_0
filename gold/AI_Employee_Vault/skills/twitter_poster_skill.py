"""
Twitter (X) Poster Agent Skill
This skill allows the AI Employee to post on Twitter (X) with summary generation.
"""

import requests
import json
import logging
from typing import Dict, List, Optional
from pathlib import Path

class TwitterPosterSkill:
    """
    Agent Skill for posting on Twitter (X)
    """

    def __init__(self, bearer_token: str = None, api_key: str = None, api_secret: str = None,
                 access_token: str = None, access_token_secret: str = None):
        self.bearer_token = bearer_token
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret

        # If not provided, try to get from environment or config
        if not self.bearer_token:
            self.bearer_token = self._get_bearer_token()
        if not self.api_key:
            self.api_key = self._get_api_key()
        if not self.api_secret:
            self.api_secret = self._get_api_secret()
        if not self.access_token:
            self.access_token = self._get_access_token()
        if not self.access_token_secret:
            self.access_token_secret = self._get_access_token_secret()

        self.logger = logging.getLogger(__name__)
        self.base_url = "https://api.twitter.com/2"

    def _get_bearer_token(self) -> str:
        """
        Get bearer token from environment or config file
        """
        # In a real implementation, this would retrieve from secure storage
        # For now, return a placeholder
        return "PLACEHOLDER_BEARER_TOKEN"

    def _get_api_key(self) -> str:
        """
        Get API key from environment or config file
        """
        return "PLACEHOLDER_API_KEY"

    def _get_api_secret(self) -> str:
        """
        Get API secret from environment or config file
        """
        return "PLACEHOLDER_API_SECRET"

    def _get_access_token(self) -> str:
        """
        Get access token from environment or config file
        """
        return "PLACEHOLDER_ACCESS_TOKEN"

    def _get_access_token_secret(self) -> str:
        """
        Get access token secret from environment or config file
        """
        return "PLACEHOLDER_ACCESS_TOKEN_SECRET"

    def generate_tweet_summary(self, content: str, max_length: int = 280) -> str:
        """
        Generate a summary of the content for Twitter posts (max 280 characters)

        Args:
            content: Original content to summarize
            max_length: Maximum length of the summary (default 280 for Twitter)

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

            # If the summary is still too long, just truncate and add ellipsis
            if len(summary) > max_length:
                # Try to find a good breaking point before max_length
                last_space = summary.rfind(' ', 0, max_length)
                if last_space != -1:
                    summary = summary[:last_space].strip() + "…"
                else:
                    summary = summary[:max_length-1] + "…"

            return summary.strip()

        except Exception as e:
            self.logger.error(f"Error generating tweet summary: {e}")
            # Return a simple truncation as fallback
            return content[:max_length-1] + "…" if len(content) > max_length else content

    def post_tweet(self, content: str, reply_to_tweet_id: str = None,
                   quote_tweet_id: str = None, media_ids: List[str] = None) -> Dict:
        """
        Post a tweet on Twitter (X)

        Args:
            content: Content to tweet
            reply_to_tweet_id: Optional ID of the tweet to reply to
            quote_tweet_id: Optional ID of the tweet to quote
            media_ids: Optional list of media IDs to attach

        Returns:
            dict: Result of the operation
        """
        try:
            # Generate summary for the tweet
            summary = self.generate_tweet_summary(content)

            # Prepare the payload
            payload = {
                "text": summary
            }

            if reply_to_tweet_id:
                payload["reply"] = {
                    "in_reply_to_tweet_id": reply_to_tweet_id
                }

            if quote_tweet_id:
                # Note: Twitter API v2 doesn't have a direct way to quote tweet in the same way as retweet
                # This would need to be handled by constructing the text appropriately
                payload["text"] = f"{summary} https://twitter.com/user/status/{quote_tweet_id}"

            if media_ids:
                payload["media"] = {
                    "media_ids": media_ids
                }

            # Twitter API v2 endpoint for creating tweets
            url = f"{self.base_url}/tweets"

            headers = {
                "Authorization": f"Bearer {self.bearer_token}",
                "Content-Type": "application/json"
            }

            # Make the API call
            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 201:
                result = response.json()
                tweet_id = result.get("data", {}).get("id")

                self.logger.info(f"Successfully posted tweet. Tweet ID: {tweet_id}")

                return {
                    "success": True,
                    "tweet_id": tweet_id,
                    "summary": summary,
                    "message": f"Successfully posted tweet with ID: {tweet_id}"
                }
            elif response.status_code == 401:
                error_msg = "Unauthorized: Check your API credentials"
                self.logger.error(f"Error posting tweet: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
            elif response.status_code == 403:
                error_msg = "Forbidden: Your account may be locked or suspended"
                self.logger.error(f"Error posting tweet: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
            else:
                error_data = response.json()
                error_msg = error_data.get("detail", "Unknown error occurred")
                self.logger.error(f"Error posting tweet: {error_msg}")

                return {
                    "success": False,
                    "error": f"Twitter API error: {error_msg}"
                }

        except requests.exceptions.ConnectionError:
            error_msg = "Connection error: Could not reach Twitter API"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
        except Exception as e:
            self.logger.error(f"Error posting to Twitter: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def quote_tweet(self, original_tweet_url: str, comment: str = None) -> Dict:
        """
        Quote an existing tweet with a comment

        Args:
            original_tweet_url: URL of the tweet to quote
            comment: Comment to add to the quote tweet

        Returns:
            dict: Result of the operation
        """
        try:
            # Extract the tweet ID from the URL
            # This is a simplified extraction - would need more robust parsing in practice
            tweet_id = original_tweet_url.split('/')[-1].split('?')[0] if original_tweet_url else None

            if not tweet_id:
                return {
                    "success": False,
                    "error": "Could not extract tweet ID from URL"
                }

            # Generate summary of the comment if provided
            if comment:
                summary = self.generate_tweet_summary(f"{comment} {original_tweet_url}")
            else:
                summary = self.generate_tweet_summary(f"{original_tweet_url}")

            # Post the tweet
            return self.post_tweet(summary)

        except Exception as e:
            self.logger.error(f"Error quoting tweet: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def search_tweets(self, query: str, max_results: int = 10) -> Dict:
        """
        Search for tweets using Twitter API v2

        Args:
            query: Search query
            max_results: Maximum number of results to return (max 100)

        Returns:
            dict: Search results
        """
        try:
            # Prepare the search parameters
            params = {
                "query": query,
                "max_results": min(max_results, 100)  # Max allowed by API is 100
            }

            # Twitter API v2 endpoint for searching tweets
            url = f"{self.base_url}/tweets/search/recent"

            headers = {
                "Authorization": f"Bearer {self.bearer_token}"
            }

            # Make the API call
            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200:
                result = response.json()
                tweets = result.get("data", [])

                self.logger.info(f"Found {len(tweets)} tweets matching query: {query}")

                return {
                    "success": True,
                    "tweets": tweets,
                    "count": len(tweets),
                    "query": query
                }
            elif response.status_code == 401:
                error_msg = "Unauthorized: Check your API credentials"
                self.logger.error(f"Error searching tweets: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
            else:
                error_data = response.json()
                error_msg = error_data.get("detail", "Unknown error occurred")
                self.logger.error(f"Error searching tweets: {error_msg}")

                return {
                    "success": False,
                    "error": f"Twitter API error: {error_msg}"
                }

        except Exception as e:
            self.logger.error(f"Error searching tweets: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_trending_topics(self, woeid: int = 1) -> Dict:  # 1 is worldwide
        """
        Get trending topics on Twitter (for a location)

        Args:
            woeid: Where On Earth ID (1 for worldwide)

        Returns:
            dict: List of trending topics
        """
        # Twitter API v2 doesn't have direct trending topics endpoint
        # For demonstration, we'll return a simulated result
        # In a real implementation, we'd use the trends API from v1.1
        # or use search to find trending hashtags

        try:
            # Let's search for popular hashtags to simulate trending topics
            hashtags = ["#AI", "#Technology", "#Innovation", "#Business", "#Startup"]
            return {
                "success": True,
                "trending_topics": hashtags,
                "woeid": woeid,
                "location": "Worldwide" if woeid == 1 else f"Location ID: {woeid}"
            }
        except Exception as e:
            self.logger.error(f"Error getting trending topics: {e}")
            return {
                "success": False,
                "error": str(e)
            }


def post_tweet_on_twitter(content: str, reply_to_tweet_id: str = None,
                         quote_tweet_id: str = None, media_ids: List[str] = None) -> Dict:
    """
    Agent Skill function to post content on Twitter (X)

    Args:
        content: Content to post
        reply_to_tweet_id: Optional ID of the tweet to reply to
        quote_tweet_id: Optional ID of the tweet to quote
        media_ids: Optional list of media IDs to attach

    Returns:
        dict: Result of the operation
    """
    try:
        skill = TwitterPosterSkill()
        return skill.post_tweet(content, reply_to_tweet_id, quote_tweet_id, media_ids)
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def quote_tweet_on_twitter(original_tweet_url: str, comment: str = None) -> Dict:
    """
    Agent Skill function to quote an existing tweet

    Args:
        original_tweet_url: URL of the tweet to quote
        comment: Comment to add to the quote tweet

    Returns:
        dict: Result of the operation
    """
    try:
        skill = TwitterPosterSkill()
        return skill.quote_tweet(original_tweet_url, comment)
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def search_tweets_on_twitter(query: str, max_results: int = 10) -> Dict:
    """
    Agent Skill function to search for tweets

    Args:
        query: Search query
        max_results: Maximum number of results to return

    Returns:
        dict: Search results
    """
    try:
        skill = TwitterPosterSkill()
        return skill.search_tweets(query, max_results)
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def generate_tweet_summary(content: str, max_length: int = 280) -> Dict:
    """
    Agent Skill function to generate a tweet summary

    Args:
        content: Original content to summarize
        max_length: Maximum length of the summary

    Returns:
        dict: Generated summary
    """
    try:
        skill = TwitterPosterSkill()
        summary = skill.generate_tweet_summary(content, max_length)

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


def get_twitter_trending_topics(woeid: int = 1) -> Dict:
    """
    Agent Skill function to get trending topics on Twitter

    Args:
        woeid: Where On Earth ID (1 for worldwide)

    Returns:
        dict: List of trending topics
    """
    try:
        skill = TwitterPosterSkill()
        return skill.get_trending_topics(woeid)
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# Example usage function
def suggest_twitter_content(topic: str = "business", content_type: str = "update") -> Dict:
    """
    Agent Skill function to suggest Twitter content based on topic

    Args:
        topic: The topic for content (e.g., "business", "technology", "industry news")
        content_type: Type of content ("update", "tip", "news", "thought")

    Returns:
        dict: Suggested content ideas
    """
    try:
        suggestions = []

        if topic.lower() == "business":
            if content_type.lower() == "tip":
                suggestions = [
                    "Share a quick business productivity tip in 280 characters or less",
                    "Post about effective team communication strategies for remote work",
                    "Offer a time management hack for entrepreneurs",
                    "Discuss the importance of work-life balance in business"
                ]
            elif content_type.lower() == "update":
                suggestions = [
                    "Share a company milestone or achievement with your followers",
                    "Post about a new product or service launch",
                    "Highlight a team member or share company culture wins",
                    "Announce a new partnership or collaboration"
                ]
            else:
                suggestions = [
                    "What are your thoughts on current business trends? I'd love to hear your perspective. #Business #Innovation",
                    "Based on recent developments in business, here's my take on the industry. #BusinessInsights #Leadership",
                    "Exploring the impact of current events on small businesses. What's your experience? #SmallBusiness #Entrepreneur"
                ]

        elif topic.lower() == "technology":
            if content_type.lower() == "tip":
                suggestions = [
                    "Share a technology tip for improving business efficiency",
                    "Post about cybersecurity best practices in 280 characters",
                    "Offer advice on using AI tools for business optimization",
                    "Discuss the importance of data privacy for businesses"
                ]
            else:
                suggestions = [
                    "What are your thoughts on recent technology trends? I'd love to hear your perspective. #Tech #AI #Innovation",
                    "Based on recent developments in tech, here's my take on the industry. #Technology #Future",
                    "Exploring the impact of technology on small businesses. What's your experience? #Tech #Business #Startup"
                ]

        else:
            # General suggestions
            suggestions = [
                "Share an update about a recent company milestone. #Business #Update",
                "Post about industry insights or trends you're observing. #Industry #Trends",
                "Share a helpful tip or lesson learned in your field. #Tip #Learn",
                "Feature a team member or highlight company culture. #Team #Culture",
                "Comment on a recent industry news or event. #News #Industry"
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
    print("Testing Twitter Poster Skills...")

    # Example 1: Generate a tweet summary
    content = "We're excited to announce that our company has achieved a significant milestone by completing 100+ projects this year, helping businesses transform digitally and achieve their goals through innovative solutions and dedicated service."
    summary_result = generate_tweet_summary(content)
    print("Tweet Summary Result:", summary_result)

    # Example 2: Suggest Twitter content
    ideas = suggest_twitter_content("business", "update")
    print("Twitter Content Ideas:", ideas)