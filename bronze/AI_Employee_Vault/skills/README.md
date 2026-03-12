# AI Employee Skills

All AI functionality should be implemented as Agent Skills as mentioned in the requirements.

This directory is reserved for Claude Code Agent Skills that will be used by the AI Employee.

## Available Skills

### vault_read.skill.py
Contains all functionality for reading from the Obsidian vault including reading Dashboard.md, Company_Handbook.md, and other vault files.

### vault_write.skill.py
Contains all functionality for writing to the Obsidian vault including updating dashboard fields, creating task files, and managing vault content.

### watcher.skill.py
Contains file system watching functionality to monitor for new files dropped in the Drop_Folder and trigger appropriate actions.

### workflow.skill.py
Handles the folder workflow automation: moving items from /Inbox → /Needs_Action → /Done as part of the AI Employee process.

### logging.skill.py
Provides comprehensive logging functionality to keep track of all actions (what was read, written, moved) with error handling and retry mechanisms.
