# AI Employee Vault - Gold Tier

Welcome to your AI Employee Vault! This system implements a Gold Tier autonomous employee that handles your personal and business affairs 24/7 with advanced capabilities including financial automation, social media management, and autonomous reasoning loops.

## 🚀 Gold Tier Features

### ✅ All Silver Tier Features
- Obsidian vault with Dashboard.md and Company_Handbook.md
- Basic folder structure: /Inbox, /Needs_Action, /Done, /Plans, /Pending_Approval, /Logs
- File system monitoring via filesystem_watcher.py
- Claude Code integration for reading/writing to the vault
- All AI functionality implemented as Agent Skills
- Gmail, WhatsApp, and LinkedIn watchers
- Claude reasoning loop with structured planning
- MCP servers for external actions (Email, Browser, Payment)
- Human-in-the-loop approval workflow
- Basic scheduling and reporting

### ✅ Odoo Community Accounting Integration
- **Odoo Accounting Skill**: Full integration with self-hosted Odoo Community via JSON-RPC
- **Invoice Management**: Create, search, and track invoices automatically
- **Customer Management**: Create and search customer records
- **Expense Tracking**: Record and categorize business expenses
- **Financial Reporting**: Access to account balances and financial data

### ✅ Multi-Platform Social Media Management
- **Facebook & Instagram Poster Skills**: Cross-platform posting capabilities
- **Twitter (X) Integration**: Automated posting with proper character limits
- **Content Generation**: AI-powered content suggestions and summaries
- **Cross-Posting**: Single operation posts to multiple platforms
- **Content Strategy**: Trending topic integration and content planning

### ✅ Ralph-Wiggum Autonomous Multi-Step Loop
- **Advanced Reasoning**: Multi-step task execution with planning and adaptation
- **Task Prioritization**: Dynamic task ordering based on priority and dependencies
- **Skill Orchestration**: Automatic selection and execution of appropriate skills
- **Adaptation Logic**: Error recovery and alternative execution paths
- **Continuous Operation**: 24/7 autonomous task processing

### ✅ Enhanced Skill Architecture
- **Modular Skills**: All AI functionality as reusable, modular skills
- **Odoo Integration Skills**: Accounting, invoicing, and customer management
- **Social Media Skills**: LinkedIn, Facebook, Instagram, and Twitter posting
- **Financial Automation Skills**: Expense tracking and reporting
- **Extensible Framework**: Easy addition of new skills

### ✅ Advanced MCP Integration
- **Browser MCP Server**: Web automation for payment portals and banking
- **Payment MCP Server**: Secure payment processing workflow
- **Email MCP Server**: Advanced email handling with attachments
- **Odoo MCP Interface**: Direct integration with accounting system

## 📁 Folder Structure

```
AI_Employee_Vault/
├── Dashboard.md           # Real-time summary
├── Company_Handbook.md    # Business rules and guidelines
├── Inbox/                 # Incoming items
├── Needs_Action/          # Items requiring processing
├── Plans/                 # Action plans created by AI
├── Done/                  # Completed items
├── Pending_Approval/      # Items requiring human approval
├── Approved/              # Approved items
├── Rejected/              # Rejected items
├── Logs/                  # System logs
├── Briefings/             # Daily/weekly briefings
├── Reports/               # Generated reports
├── Drop_Folder/           # Monitored folder for new files
├── skills/                # AI Agent Skills
├── skills/odoo_accounting_skill.py      # Odoo accounting integration
├── skills/facebook_ig_poster_skill.py   # Facebook/Instagram automation
├── skills/twitter_poster_skill.py       # Twitter/X automation
├── skills/linkedin_poster.py            # LinkedIn automation
├── ralph_wiggum_loop.py   # Autonomous multi-step loop
├── *.py                   # System components
└── README.md              # This file
```

## 📁 Folder Structure

```
AI_Employee_Vault/
├── Dashboard.md           # Real-time summary
├── Company_Handbook.md    # Business rules and guidelines
├── Inbox/                 # Incoming items
├── Needs_Action/          # Items requiring processing
├── Plans/                 # Action plans created by AI
├── Done/                  # Completed items
├── Pending_Approval/      # Items requiring human approval
├── Approved/              # Approved items
├── Rejected/              # Rejected items
├── Logs/                  # System logs
├── Briefings/             # Daily/weekly briefings
├── Reports/               # Generated reports
├── Drop_Folder/           # Monitored folder for new files
├── skills/                # AI Agent Skills
├── skills/linkedin_poster.py    # LinkedIn automation skill
├── *.py                   # System components
└── README.md              # This file
```

## 🛠️ Components

### Core Components
- `orchestrator.py`: Main orchestrator that manages all components
- `reasoning_loop.py`: AI reasoning that creates Plan.md files
- `scheduler.py`: Scheduling for recurring tasks
- `start_ai_employee.py`: Main startup script
- `ralph_wiggum_loop.py`: Advanced autonomous multi-step reasoning loop

### Watcher Components
- `base_watcher.py`: Base class for all watchers
- `filesystem_watcher.py`: Monitors file system changes
- `gmail_watcher.py`: Monitors Gmail (requires setup)
- `whatsapp_watcher.py`: Monitors WhatsApp (requires Playwright)
- `linkedin_watcher.py`: Monitors LinkedIn (requires Playwright)

### Skills
- `skills/odoo_accounting_skill.py`: Odoo Community accounting integration via JSON-RPC
- `skills/facebook_ig_poster_skill.py`: Facebook and Instagram posting with summaries
- `skills/twitter_poster_skill.py`: Twitter (X) posting with character limit management
- `skills/linkedin_poster.py`: LinkedIn posting automation

### MCP Servers
- `mcp_email_server.py`: Email sending via MCP protocol
- `mcp_browser_server.py`: Web automation for payment portals and banking
- `mcp_payment_server.py`: Secure payment processing workflow

## 📋 Setup and Usage

### Prerequisites
- Python 3.13+
- Claude Code subscription
- Obsidian (v1.10.6+)
- Node.js (v24+ LTS) for MCP servers

### Installation
1. Install required Python packages:
```bash
pip install schedule google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client playwright xmlrpc-client
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

5. For Odoo integration, ensure your Odoo Community instance is running and API credentials are available

6. For social media integration, obtain appropriate API tokens for Facebook, Instagram, and Twitter

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
- **Audit Logging**: All actions logged for review
- **File-Based Workflow**: Clear approval trails

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

### Multi-Platform Social Media Posting
1. Content request received → creates file in Needs_Action
2. Ralph-Wiggum loop selects appropriate social media skills
3. Content is summarized to fit platform-specific limits
4. Post is created on Facebook, Instagram, and Twitter simultaneously
5. Results are logged and reported

### Financial Task Automation
1. Invoice request received → creates file in Needs_Action
2. Ralph-Wiggum loop determines required Odoo operations
3. Customer is searched/created using Odoo skills
4. Invoice is generated and sent via MCP email server
5. Transaction is recorded in accounting system

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

- Check `orchestrator.log` and `reasoning_loop.log` for errors
- If watchers fail, verify API credentials and permissions
- For MCP server issues, check environment variables
- If Playwright-based watchers fail, ensure Chromium is installed

## 🏗️ Architecture Overview

### System Architecture
The Gold Tier AI Employee follows a modular architecture with distinct layers:

1. **Perception Layer**: Watcher scripts that monitor external sources
2. **Processing Layer**: Reasoning loop and Ralph-Wiggum autonomous loop
3. **Skills Layer**: Modular agent skills for specific functions
4. **Integration Layer**: MCP servers for external system communication
5. **Storage Layer**: File-based workflow with structured directories

### Data Flow
- External events → Watcher scripts → Needs_Action files → Reasoning loop → Plans → Skills execution → MCP servers → External actions
- The Ralph-Wiggum loop provides autonomous processing of complex multi-step tasks
- Skills are dynamically selected based on task requirements

### Security Architecture
- All sensitive operations require human approval
- API credentials are stored securely in environment variables
- Action trails are maintained through the file-based workflow
- Financial operations are double-checked through the approval process

## 📚 Lessons Learned

### Technical Insights
1. **Modular Skill Architecture**: Breaking functionality into discrete agent skills allows for better maintainability and extensibility
2. **Asynchronous Processing**: Using file-based communication between components enables reliable, decoupled processing
3. **Error Recovery**: The Ralph-Wiggum loop's adaptation capability is crucial for handling real-world edge cases
4. **API Integration Complexity**: Different platforms (Odoo, social media) require different authentication and API approaches

### Operational Learnings
1. **Human-in-the-Loop Balance**: Critical operations need approval, but too many approvals slow productivity
2. **Task Prioritization**: Dynamic prioritization based on business impact improves efficiency
3. **Cross-Platform Consistency**: Content needs to be adapted for each platform's specific characteristics
4. **Financial Accuracy**: Accounting integrations require precise data handling and validation

### Scalability Considerations
1. **Resource Management**: Browser-based automation (Playwright) consumes significant resources
2. **Rate Limiting**: Social media and API rate limits must be carefully managed
3. **Parallel Processing**: Multiple independent watchers can run in parallel, but shared resources need coordination
4. **State Management**: Persistent sessions for browsers and API tokens need careful handling

## 📞 Support

For issues with this Gold Tier implementation:
1. Check the logs in the vault directory
2. Verify all prerequisites are installed
3. Confirm environment variables are set correctly
4. Test individual components separately if needed
5. For Odoo integration issues, verify server connectivity and API permissions
6. For social media issues, check API token validity and rate limits