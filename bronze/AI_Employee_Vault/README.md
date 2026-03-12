# AI Employee Bronze Tier Implementation

## Overview
This is the Bronze Tier implementation of the Personal AI Employee as described in the hackathon document. It includes:
- Obsidian vault structure with required files
- Basic folder structure (Inbox, Needs_Action, Done)
- Filesystem watcher to monitor for new files
- Orchestrator to process tasks

## Prerequisites
- Python 3.8 or higher
- Claude Code (for higher tier integration)
- Required Python packages: `watchdog`

## Setup

1. Install required packages:
```bash
pip install watchdog
```

2. The vault structure is already created with the following folders:
   - `Inbox/` - For incoming items (not used in Bronze Tier)
   - `Needs_Action/` - For items requiring processing
   - `Done/` - For completed items
   - `Plans/` - For future implementation
   - `Pending_Approval/` - For future implementation
   - `Logs/` - For system logs

3. The following files are pre-configured:
   - `Dashboard.md` - Real-time summary of activities
   - `Company_Handbook.md` - Rules and guidelines for the AI Employee
   - `base_watcher.py` - Template for all watcher implementations
   - `filesystem_watcher.py` - Monitors Drop_Folder for new files
   - `orchestrator.py` - Main process that coordinates all components

## How to Run

1. Start the orchestrator:
```bash
python orchestrator.py
```

2. Place files in the `Drop_Folder/` directory to trigger the system
3. The filesystem watcher will detect new files and create action files in `Needs_Action/`
4. The orchestrator will process these files and move them to `Done/`

## Bronze Tier Features

- ✅ Obsidian vault with Dashboard.md and Company_Handbook.md
- ✅ Basic folder structure: /Inbox, /Needs_Action, /Done
- ✅ File system monitoring watcher
- ✅ Claude Code can read from and write to the vault (ready for integration)
- ✅ All AI functionality ready to be implemented as Agent Skills

## Next Steps (Silver/Gold Tiers)

- Add more watcher types (Gmail, WhatsApp)
- Integrate Claude Code for reasoning
- Add MCP servers for external actions
- Implement the "Ralph Wiggum" persistence loop
- Add human-in-the-loop approval workflows

## File Structure
```
AI_Employee_Vault/
├── Dashboard.md
├── Company_Handbook.md
├── base_watcher.py
├── filesystem_watcher.py
├── orchestrator.py
├── Drop_Folder/        # Where to place files for processing
├── Inbox/
├── Needs_Action/       # Files requiring action
├── Done/              # Processed files
├── Plans/
├── Pending_Approval/
└── Logs/
```