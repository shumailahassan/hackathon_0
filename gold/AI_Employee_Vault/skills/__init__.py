"""
AI Employee Skills Module
This module contains all the modular skills for the Silver Tier AI Employee
"""

from .linkedin_poster import post_business_update, suggest_business_post_ideas
import logging


def get_all_skills():
    """
    Return a dictionary of all available skills with their descriptions.
    This allows for easy skill discovery and management.
    """
    return {
        'linkedin_post': {
            'module': 'linkedin_poster',
            'function': 'post_business_update',
            'description': 'Post business updates on LinkedIn with optional hashtags and images'
        },
        'linkedin_suggest': {
            'module': 'linkedin_poster',
            'function': 'suggest_business_post_ideas',
            'description': 'Suggest business post ideas based on trending topics'
        }
    }


def run_skill(skill_name: str, **kwargs):
    """
    Run a specific skill by name with the provided parameters.

    Args:
        skill_name: Name of the skill to run
        **kwargs: Parameters for the skill

    Returns:
        Result of the skill execution
    """
    skills = get_all_skills()

    if skill_name not in skills:
        raise ValueError(f"Skill '{skill_name}' not found. Available skills: {list(skills.keys())}")

    skill_info = skills[skill_name]

    # Map skill names to actual functions
    skill_functions = {
        'linkedin_post': post_business_update,
        'linkedin_suggest': suggest_business_post_ideas
    }

    try:
        skill_func = skill_functions[skill_name]
        return skill_func(**kwargs)
    except Exception as e:
        logging.error(f"Error running skill '{skill_name}': {e}")
        return {"success": False, "error": str(e)}


# Initialize skills module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("AI Employee Skills Module loaded successfully")