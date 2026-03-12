# init_claude_config.py
import os
import json
from pathlib import Path

def create_claude_config():
    """Create Claude Code configuration for the AI Employee vault"""

    # Create .claude directory in the vault
    vault_path = Path(__file__).parent
    claude_dir = vault_path / '.claude'
    claude_dir.mkdir(exist_ok=True)

    # Create a basic config file
    config = {
        "version": "1.0",
        "name": "AI Employee Vault",
        "description": "Personal AI Employee Hackathon Bronze Tier",
        "workingDirectory": str(vault_path),
        "filePatterns": [
            "**/*.md",
            "**/*.txt",
            "**/*.py"
        ]
    }

    config_path = claude_dir / 'config.json'
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"Created Claude Code configuration at: {config_path}")
    print("The vault is now ready for Claude Code integration.")

    # Also create a skills directory as mentioned in the requirements
    skills_dir = vault_path / 'skills'
    skills_dir.mkdir(exist_ok=True)

    # Create a placeholder skill as per the requirements
    placeholder_skill = '''# AI Employee Skills

All AI functionality should be implemented as Agent Skills as mentioned in the requirements.

This directory is reserved for Claude Code Agent Skills that will be used by the AI Employee.
'''
    with open(skills_dir / 'README.md', 'w') as f:
        f.write(placeholder_skill)

    print(f"Created skills directory at: {skills_dir}")
    print("Skills can be added here for Bronze Tier requirement compliance.")

if __name__ == "__main__":
    create_claude_config()