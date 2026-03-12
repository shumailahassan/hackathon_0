---
id: 2
title: "AI Employee Vault Comprehensive Project Overview"
stage: "general"
date_iso: "2026-02-24"
surface: "agent"
model: "if/qwen3-coder-plus"
feature: "ai-employee-vault"
branch: "master"
user: "HC"
command: "create a phr file of my whole project"
labels: ["project-overview", "silver-tier", "ai-employee", "architecture", "system-documentation"]
links:
  spec: null
  ticket: null
  adr: "history/adr/1-silver-tier-architecture.md"
  pr: null
files_yaml: |
  - AI_Employee_Vault/README.md
  - AI_Employee_Vault/start_ai_employee.py
  - AI_Employee_Vault/orchestrator.py
  - AI_Employee_Vault/reasoning_loop.py
  - AI_Employee_Vault/scheduler.py
  - AI_Employee_Vault/base_watcher.py
  - AI_Employee_Vault/filesystem_watcher.py
  - AI_Employee_Vault/gmail_watcher.py
  - AI_Employee_Vault/whatsapp_watcher.py
  - AI_Employee_Vault/linkedin_watcher.py
  - AI_Employee_Vault/mcp_email_server.py
  - AI_Employee_Vault/skills/linkedin_poster.py
  - AI_Employee_Vault/Company_Handbook.md
  - AI_Employee_Vault/Dashboard.md
  - AI_Employee_Vault/SILVER_TIER_COMPLETED.md
tests_yaml: |
  - "python start_ai_employee.py ."
  - "python orchestrator.py ."
  - "python scheduler.py ."
  - "Import tests for all modules"
  - "File drop and processing workflow test"
  - "End-to-end system functionality test"
prompt_text: |
  create a phr file of my whole project
response_text: |
  Comprehensive documentation of the AI Employee Vault (Silver Tier) project, including:
  - Architecture overview and component structure
  - File-based workflow system
  - Watcher components and their functionality
  - Reasoning loop and planning system
  - Skills and MCP integration
  - Folder structure and data flow
  - System capabilities and functionality
outcome: |
  Complete documentation of the AI Employee Vault system including architecture, components, functionality, and operational workflow. The PHR captures the entire project structure and capabilities.
evaluation: "Complete project documentation created with all components and architecture documented"
---

# AI Employee Vault (Silver Tier) - Comprehensive Project Overview

## Project Summary

The AI Employee Vault is a Silver Tier autonomous employee system designed to handle personal and business affairs 24/7. The system implements an advanced file-based workflow with multiple watchers, reasoning loops, scheduling, and human-in-the-loop approval workflows.

## Architecture Overview

The system follows a component-based architecture with the following key elements:

1. **Orchestrator Pattern**: Central coordinator managing all system components
2. **File-Based Communication**: Components communicate through structured file placement
3. **Watcher Architecture**: Specialized watchers monitor different inputs
4. **Reasoning Loop**: Central AI component creating structured plans
5. **MCP Protocol Integration**: Model Context Protocol for external actions

## Folder Structure

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
├── *.py                   # System components
└── README.md              # Documentation
```

## Core Components

### 1. **start_ai_employee.py**
Main startup script that coordinates all system components. Implements process monitoring and restart capabilities.

### 2. **orchestrator.py**
Central orchestrator that manages all components including watchers, reasoning loop, and file processing workflows.

### 3. **reasoning_loop.py**
AI reasoning component that creates Plan.md files from Needs_Action items with structured action steps, timelines, and success criteria.

### 4. **scheduler.py**
Scheduling system for recurring tasks including daily briefings, weekly audits, social media scheduling, and report generation.

### 5. **mcp_email_server.py**
Email sending via MCP protocol with proper authentication and support for attachments and bulk emails.

## Watcher Components

### 1. **base_watcher.py**
Base class for all watchers providing common functionality and interface.

### 2. **filesystem_watcher.py**
Monitors file system changes, particularly the Drop_Folder for new files.

### 3. **gmail_watcher.py**
Monitors Gmail for new emails (requires Google API setup).

### 4. **whatsapp_watcher.py**
Monitors WhatsApp for business messages using Playwright for web automation.

### 5. **linkedin_watcher.py**
Monitors LinkedIn for business opportunities using Playwright for web automation.

## Skills System

### **skills/linkedin_poster.py**
LinkedIn automation skill for generating and posting business-related content based on trending topics.

## Workflow System

The system implements a sophisticated file-based workflow:

1. **Perception**: Watchers monitor external sources and create files in Needs_Action folder
2. **Action Creation**: Watchers generate structured files with context and requirements
3. **Reasoning**: The reasoning loop creates detailed Plan.md files with steps, priorities, and timelines
4. **Approval**: Sensitive actions create approval requests in Pending_Approval folder
5. **Execution**: Approved actions are executed via MCP servers
6. **Reporting**: System updates Dashboard.md and creates reports

## File Processing Example

The system has successfully processed files as demonstrated by:
- Files in Needs_Action/: `FILE_test_file.txt` (53 bytes)
- Plans in Plans/: `PLAN_FILE_test_file_20260223_055939.md`
- Completed tasks in Done/: `FILE_test_file.md`

## Configuration and Setup

### Prerequisites:
- Python 3.13+
- Claude Code subscription
- Obsidian (v1.10.6+)
- Node.js (v24+ LTS) for MCP servers

### Required Packages:
- schedule==1.2.0
- google-auth==2.23.4
- google-auth-oauthlib==1.1.0
- google-auth-httplib2==0.1.1
- google-api-python-client==2.108.0
- playwright==1.40.0
- watchdog==4.0.1

## Security Features

- Human approval for financial transactions and social media posts
- Credential management via environment variables
- Audit logging for all actions
- File-based approval trails
- Segregation of duties for sensitive operations

## System Capabilities

### Silver Tier Features:
- [x] All Bronze Tier Features
- [x] Multiple Watcher Scripts (Filesystem, Gmail, WhatsApp, LinkedIn)
- [x] Automatic LinkedIn Posting
- [x] Claude Reasoning Loop
- [x] MCP Server for External Actions
- [x] Human-in-the-Loop Approval Workflow
- [x] Basic Scheduling
- [x] Agent Skills Implementation

### Example Workflows:
1. **Email Response Workflow**: Gmail watcher → Needs_Action → Reasoning loop → MCP server
2. **LinkedIn Business Development**: LinkedIn watcher → Plan creation → Approval → LinkedIn posting
3. **Task Automation**: File drop → Filesystem watcher → Reasoning loop → Execution

## Status Indicators
- 🟢 **Active**: System components running
- 🟡 **Pending**: Awaiting human approval
- 🔵 **Processing**: Tasks being executed
- 🟣 **Scheduled**: Tasks queued for future execution

## Generated Files and Reports

The system has produced:
- Daily briefings in Briefings/ folder
- Plans in Plans/ folder (5 plans created)
- Completed tasks in Done/ folder (6 completed tasks)
- Weekly reports in Reports/ folder
- Dashboard updates in Dashboard.md

## System Status

The AI Employee Vault system is fully functional with all Silver Tier capabilities operational. The system demonstrates complete workflow functionality from perception to action execution with proper approval processes and documentation.