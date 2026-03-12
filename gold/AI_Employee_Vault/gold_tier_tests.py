"""
Gold Tier Component Tests
Basic validation tests for the new Gold Tier components
"""

import unittest
import os
import sys
from pathlib import Path

# Add the skills directory to the path
sys.path.insert(0, str(Path(__file__).parent / "skills"))

class TestGoldTierComponents(unittest.TestCase):
    """Test class for Gold Tier components"""

    def setUp(self):
        """Set up test environment"""
        self.vault_path = Path(__file__).parent
        self.skills_path = self.vault_path / "skills"

    def test_odoo_accounting_skill_exists(self):
        """Test that Odoo accounting skill exists"""
        skill_path = self.skills_path / "odoo_accounting_skill.py"
        self.assertTrue(skill_path.exists(), f"Odoo accounting skill not found at {skill_path}")

    def test_facebook_ig_poster_skill_exists(self):
        """Test that Facebook/Instagram poster skill exists"""
        skill_path = self.skills_path / "facebook_ig_poster_skill.py"
        self.assertTrue(skill_path.exists(), f"Facebook/Instagram poster skill not found at {skill_path}")

    def test_twitter_poster_skill_exists(self):
        """Test that Twitter poster skill exists"""
        skill_path = self.skills_path / "twitter_poster_skill.py"
        self.assertTrue(skill_path.exists(), f"Twitter poster skill not found at {skill_path}")

    def test_ralph_wiggum_loop_exists(self):
        """Test that Ralph-Wiggum loop exists"""
        loop_path = self.vault_path / "ralph_wiggum_loop.py"
        self.assertTrue(loop_path.exists(), f"Ralph-Wiggum loop not found at {loop_path}")

    def test_skills_importable(self):
        """Test that skills can be imported without errors"""
        try:
            from skills import odoo_accounting_skill
            from skills import facebook_ig_poster_skill
            from skills import twitter_poster_skill
            # Just check that the modules can be imported
            self.assertTrue(hasattr(odoo_accounting_skill, 'create_invoice_in_odoo'))
            self.assertTrue(hasattr(facebook_ig_poster_skill, 'post_to_facebook_page'))
            self.assertTrue(hasattr(twitter_poster_skill, 'post_tweet_on_twitter'))
        except ImportError as e:
            self.fail(f"Failed to import skills: {e}")

    def test_skills_directory_structure(self):
        """Test that skills directory has proper structure"""
        expected_skills = [
            "odoo_accounting_skill.py",
            "facebook_ig_poster_skill.py",
            "twitter_poster_skill.py",
            "linkedin_poster.py"
        ]

        for skill in expected_skills:
            skill_path = self.skills_path / skill
            self.assertTrue(skill_path.exists(), f"Expected skill {skill} not found")

    def test_readme_updated(self):
        """Test that README.md has been updated with Gold Tier features"""
        readme_path = self.vault_path / "README.md"
        self.assertTrue(readme_path.exists(), "README.md not found")

        content = readme_path.read_text(encoding='utf-8', errors='ignore')

        # Check for Gold Tier indicators
        gold_tier_indicators = [
            "Gold Tier",
            "Odoo Community Accounting Integration",
            "Multi-Platform Social Media Management",
            "Ralph-Wiggum Autonomous Multi-Step Loop",
            "ralph_wiggum_loop.py",
            "odoo_accounting_skill.py",
            "facebook_ig_poster_skill.py",
            "twitter_poster_skill.py",
            "Architecture Overview",
            "Lessons Learned"
        ]

        for indicator in gold_tier_indicators:
            self.assertIn(indicator, content, f"'{indicator}' not found in README.md")

    def test_basic_functionality_of_skills(self):
        """Test basic functionality of skills (without real API calls)"""
        # Import the skills
        try:
            from skills.facebook_ig_poster_skill import FacebookIGPosterSkill
            from skills.twitter_poster_skill import TwitterPosterSkill

            # Test instantiation (avoid Odoo skill that requires connection)
            fb_ig_skill = FacebookIGPosterSkill()
            twitter_skill = TwitterPosterSkill()

            # Test summary generation methods
            test_content = "This is a test content for summary generation. It should be shortened appropriately."

            fb_ig_summary = fb_ig_skill.generate_post_summary(test_content, max_length=50)
            twitter_summary = twitter_skill.generate_tweet_summary(test_content, max_length=50)

            # Check that summaries are generated and are within length limits
            self.assertLessEqual(len(fb_ig_summary), 50)
            self.assertLessEqual(len(twitter_summary), 50)

            # Check that summaries contain meaningful content
            self.assertTrue(len(fb_ig_summary) > 0)
            self.assertTrue(len(twitter_summary) > 0)

            # Test that the skills have the expected methods
            self.assertTrue(hasattr(fb_ig_skill, 'generate_post_summary'))
            self.assertTrue(hasattr(twitter_skill, 'generate_tweet_summary'))

        except Exception as e:
            self.fail(f"Error testing basic functionality: {e}")


def run_validation_report():
    """Generate a validation report"""
    print("=" * 60)
    print("GOLD TIER VALIDATION REPORT")
    print("=" * 60)

    # Test if all required components exist
    vault_path = Path(__file__).parent
    skills_path = vault_path / "skills"

    components = {
        "odoo_accounting_skill.py": skills_path / "odoo_accounting_skill.py",
        "facebook_ig_poster_skill.py": skills_path / "facebook_ig_poster_skill.py",
        "twitter_poster_skill.py": skills_path / "twitter_poster_skill.py",
        "ralph_wiggum_loop.py": vault_path / "ralph_wiggum_loop.py",
        "README.md updated": vault_path / "README.md"
    }

    results = {}
    for name, path in components.items():
        exists = path.exists()
        results[name] = exists
        status = "[PASS]" if exists else "[FAIL]"
        print(f"{status} {name}: {'Found' if exists else 'Missing'}")

    print("\nRunning basic functionality tests...")

    # Create a test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestGoldTierComponents)

    # Run the tests directly without suppressing output
    print("\nDetailed test results:")
    runner_verbose = unittest.TextTestRunner(verbosity=2)
    result_verbose = runner_verbose.run(suite)

    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    all_found = all(results.values())
    all_passed = result_verbose.wasSuccessful()

    print(f"Components present: {'[PASS]' if all_found else '[FAIL]'}")
    print(f"Tests passed: {'[PASS]' if all_passed else '[FAIL]'}")

    if all_found and all_passed:
        print("\n[PASS] GOLD TIER VALIDATION: ALL SYSTEMS OPERATIONAL")
        print("[PASS] All required components are present")
        print("[PASS] All basic functionality tests passed")
        print("[PASS] AI Employee Gold Tier is ready for production")
        return True
    else:
        print("\n[FAIL] GOLD TIER VALIDATION: ISSUES FOUND")
        if not all_found:
            print("- Missing components detected")
        if not all_passed:
            print("- Test failures detected")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "validate":
        success = run_validation_report()
        sys.exit(0 if success else 1)
    else:
        # Run tests with output
        unittest.main(verbosity=2)