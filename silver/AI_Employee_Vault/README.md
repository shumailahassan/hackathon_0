# AI Employee Vault - Silver Tier

Welcome to your AI Employee Vault! This system implements a Silver Tier autonomous employee that handles your personal and business affairs 24/7.

## 🚀 Silver Tier Features

### ✅ All Bronze Tier Features
- Obsidian vault with Dashboard.md and Company_Handbook.md
- Basic folder structure: /Inbox, /Needs_Action, /Done, /Plans, /Pending_Approval, /Logs
- File system monitoring via filesystem_watcher.py
- Claude Code integration for reading/writing to the vault
- All AI functionality implemented as Agent Skills

### ✅ Two or More Watcher Scripts
- **Filesystem Watcher**: Monitors Drop_Folder for new files
- **Gmail Watcher**: Monitors Gmail for new emails (requires setup)
- **WhatsApp Watcher**: Monitors WhatsApp for business messages (requires Playwright)
- **LinkedIn Watcher**: Monitors LinkedIn for business opportunities (requires Playwright)

### ✅ Automatic LinkedIn Posting
- **LinkedIn Poster Skill**: Automatically generate and post business-related content
- **Trending Topic Integration**: Suggests content based on trending LinkedIn topics
- **Business Promotion**: Helps generate sales through strategic posting

### ✅ Claude Reasoning Loop
- **Reasoning Loop**: Creates Plan.md files from Needs_Action items
- **Structured Planning**: Generates detailed action plans with steps, priorities, and timelines
- **Company Handbook Integration**: Follows company rules when creating plans

### ✅ MCP Server for External Actions
- **Email MCP Server**: Send emails via SMTP with proper authentication
- **Model Context Protocol**: Follows MCP standards for AI external actions
- **Secure Email Transmission**: Handles attachments and bulk emails

### ✅ Human-in-the-Loop Approval Workflow
- **Approval Requests**: Critical actions require human approval
- **File-Based Workflow**: Approval files in Pending_Approval folder
- **Segregation of Duties**: Sensitive actions need explicit approval

### ✅ Basic Scheduling
- **Daily Briefings**: Morning business summaries
- **Weekly Audits**: Business and financial reviews
- **Social Media Scheduling**: Regular posting tasks
- **Report Generation**: Weekly performance reports

### ✅ Agent Skills Implementation
- All AI functionality implemented as modular Agent Skills
- LinkedIn poster skill for social media automation
- Extensible architecture for additional skills

## 📁 Folder Structure

```
AI_Employee_Vault/
├── Dashboard.md              # Real-time summary
├── Company_Handbook.md       # Business rules and guidelines
├── Inbox/                    # Incoming items
├── Needs_Action/             # Items requiring processing
├── Plans/                    # Action plans created by AI
├── Done/                     # Completed items
├── Pending_Approval/         # Items requiring human approval
├── Approved/                 # Approved items
├── Rejected/                 # Rejected items
├── Logs/                     # System logs
├── Briefings/                # Daily/weekly briefings
├── Reports/                  # Generated reports
├── Drop_Folder/              # Monitored folder for new files
├── skills/                   # AI Agent Skills directory
│   └── linkedin_poster.py    # LinkedIn automation skill
├── orchestrator.py           # Main orchestrator
├── reasoning_loop.py         # AI reasoning engine
├── scheduler.py              # Task scheduler
├── start_ai_employee.py      # Main startup script
├── *.py                      # System components
│   ├── base_watcher.py       # Base class for all watchers
│   ├── filesystem_watcher.py # File system monitoring
│   ├── gmail_watcher.py      # Gmail integration
│   ├── whatsapp_watcher.py   # WhatsApp integration
│   └── linkedin_watcher.py   # LinkedIn integration
├── mcp_email_server.py       # MCP email server
└── README.md                 # This file
```

## 🛠️ Components

### Core Components
- `orchestrator.py`: Main orchestrator that manages all components with multi-threading
- `reasoning_loop.py`: AI reasoning engine that creates structured Plan.md files
- `scheduler.py`: Task scheduler for recurring business activities
- `start_ai_employee.py`: Centralized startup script for the entire system

### Watcher Components
- `base_watcher.py`: Abstract base class for all watchers
- `filesystem_watcher.py`: File system monitoring with real-time updates
- `gmail_watcher.py`: Monitors Gmail for new emails using Google API
- `whatsapp_watcher.py`: Monitors WhatsApp for business messages using Playwright
- `linkedin_watcher.py`: Monitors LinkedIn for business opportunities using Playwright

### Agent Skills
- `skills/linkedin_poster.py`: LinkedIn posting automation with trending topics

### MCP Servers
- `mcp_email_server.py`: Email sending via MCP protocol with SMTP authentication

## 📋 Setup and Usage

### Prerequisites
- Python 3.13+
- Claude Code subscription
- Obsidian (v1.10.6+)
- Node.js (v24+ LTS) for MCP servers

### Installation
1. Install required Python packages:
```bash
pip install schedule google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client playwright
```

2. Install Playwright browsers (for WhatsApp/LinkedIn watchers):
```bash
playwright install chromium
```

3. For Gmail integration, follow Google's API setup:
   - Go to Google Cloud Console
   - Create credentials.json for Gmail API
   - Place in vault directory

4. For MCP email server, set environment variables:
```bash
export SMTP_SERVER=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USERNAME=your_email@gmail.com
export SMTP_PASSWORD=your_app_password
export SMTP_FROM_EMAIL=your_email@gmail.com
```

### Running the System

1. **Start the complete system:**
```bash
python start_ai_employee.py
```

2. **Or start individual components:**
```bash
# Start orchestrator (includes all watchers and reasoning loop)
python orchestrator.py

# Start scheduler separately
python scheduler.py
```

### How It Works

1. **Perception**: Watchers monitor external sources (email, WhatsApp, LinkedIn, file system)
2. **Action Creation**: Watchers create files in the Needs_Action folder
3. **Reasoning**: The reasoning loop creates detailed Plan.md files
4. **Approval**: Sensitive actions create approval requests in Pending_Approval
5. **Execution**: Approved actions are executed via MCP servers
6. **Reporting**: System updates Dashboard.md and creates reports

## 🛡️ Security Features

- **Human Approval**: Financial transactions and social media posts require approval
- **Credential Management**: SMTP credentials stored in environment variables
- **Audit Logging**: All actions logged for review across all components
- **File-Based Workflow**: Clear approval trails with timestamps and status tracking
- **Modular Architecture**: Isolated components with clear boundaries

## 📊 Example Workflows

### Email Response Workflow
1. Gmail watcher detects new email → creates file in Needs_Action
2. Reasoning loop creates Plan.md with response steps
3. If sender is trusted, response might be auto-approved
4. MCP server sends response

### LinkedIn Business Development
1. LinkedIn watcher detects opportunity → creates file in Needs_Action
2. Reasoning loop creates Plan.md for engagement
3. Plan may include creating a LinkedIn post via Agent Skill
4. Post requires approval before publishing

### Task Automation
1. File dropped in Drop_Folder → detected by filesystem watcher
2. File moved to Needs_Action folder
3. Reasoning loop creates a plan to process the task
4. Plan executed with appropriate tools

## 🚦 Status Indicators

- 🟢 **Active**: System components running
- 🟡 **Pending**: Awaiting human approval
- 🔵 **Processing**: Tasks being executed
- 🟣 **Scheduled**: Tasks queued for future execution

## 🔧 Troubleshooting

- Check individual component logs (`orchestrator.log`, `reasoning_loop.log`, `scheduler.log`, etc.)
- If watchers fail, verify API credentials and permissions
- For MCP server issues, check environment variables and authentication
- If Playwright-based watchers fail, ensure Chromium is installed
- Monitor Dashboard.md for system status updates

## 🏗️ Architecture

The Silver Tier implementation follows a modular architecture:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   External      │    │   Perceptual    │    │   Decision &    │
│   Sources       │───▶│   Components    │───▶│   Reasoning     │
│  (Email, etc)   │    │ (Watchers)      │    │ (Reasoning Loop)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Approval      │    │   Execution     │    │   Feedback &    │
│   Workflow      │◀───│   Components    │───▶│   Monitoring    │
│ (Human-in-loop) │    │ (MCP Servers)   │    │ (Dashboard/Logs)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📝 Logging and Error Handling

All components implement comprehensive logging and error handling:

- **Logging**: All actions are logged with timestamps, component names, and detailed information
- **Error Handling**: Graceful degradation and recovery mechanisms
- **Audit Trail**: Complete tracking of all system operations
- **Modularity**: Clear separation of concerns with well-defined interfaces

## 📞 Support

For issues with this Silver Tier implementation:
1. Check individual component logs in the vault directory
2. Verify all prerequisites are installed
3. Confirm environment variables are set correctly
4. Test individual components separately if needed
5. Review the modular architecture for debugging specific components