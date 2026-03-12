# ADR 1: Silver Tier AI Employee System Architecture

## Status
Accepted

## Context
The AI Employee system implements a Silver Tier autonomous employee that handles personal and business affairs. The architecture needed to support multiple watchers, reasoning loops, scheduling, and human-in-the-loop approval workflows while maintaining separation of concerns and extensibility.

## Decision
We chose a component-based architecture with the following key elements:

1. **Orchestrator Pattern**: A central orchestrator manages all system components
2. **File-Based Communication**: Components communicate through structured file placement in dedicated folders (Inbox, Needs_Action, Done, etc.)
3. **Watcher Architecture**: Specialized watchers monitor different inputs (filesystem, email, social media)
4. **Reasoning Loop**: Central AI component that creates structured plans from action items
5. **MCP Protocol Integration**: Model Context Protocol for external actions

## Alternatives Considered
- Database-driven architecture: Rejected for complexity and state management
- Real-time event streaming: Rejected for complexity in the context of a file-based vault system
- Monolithic design: Rejected for lack of modularity and extensibility

## Consequences

### Positive
- Clear separation of concerns between components
- Easy debugging through file inspection
- Extensible architecture for new watchers and skills
- Human-readable workflow state
- Resilient to component failures (file-based persistence)

### Negative
- File system dependency may not scale to very high throughput
- Potential race conditions in file operations (mitigated by design)
- Requires careful file naming conventions to avoid conflicts

## Implementation
The architecture is implemented across multiple Python files:
- `orchestrator.py` - Central coordination
- Specialized watcher files (filesystem_watcher.py, gmail_watcher.py, etc.)
- `reasoning_loop.py` - AI reasoning component
- `scheduler.py` - Task scheduling
- `mcp_email_server.py` - External action protocol
- `skills/` directory - Extensible skill modules

## Validation
The architecture has been validated through:
- Successful component startup and coordination
- End-to-end file processing workflow
- Plan generation and approval workflows
- Error handling and component resilience