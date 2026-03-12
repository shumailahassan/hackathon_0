"""
Claude Reasoning Loop for creating Plan.md files
This module implements the reasoning logic that reads files from Needs_Action
and creates Plan.md files with structured action items
"""

import os
import sys
import time
import logging
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import re


class ReasoningLoop:
    """
    Modular reasoning loop with enhanced logging and error handling.
    """

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action_path = self.vault_path / 'Needs_Action'
        self.plans_path = self.vault_path / 'Plans'
        self.pending_approval_path = self.vault_path / 'Pending_Approval'
        self.company_handbook_path = self.vault_path / 'Company_Handbook.md'
        self.dashboard_path = self.vault_path / 'Dashboard.md'

        # Ensure directories exist
        self.plans_path.mkdir(exist_ok=True)
        self.pending_approval_path.mkdir(exist_ok=True)

        # Setup logging
        self.logger = self._setup_logger()

        # Initialize company rules
        self.company_rules = self.get_company_rules()

    def _setup_logger(self) -> logging.Logger:
        """Setup logger for the reasoning loop."""
        logger = logging.getLogger('reasoning_loop')
        logger.setLevel(logging.INFO)

        # Create file handler
        file_handler = logging.FileHandler('reasoning_loop.log')
        file_handler.setLevel(logging.INFO)

        # Create console handler
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to logger if not already present
        if not logger.handlers:
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)

        return logger

    def get_company_rules(self) -> Dict[str, Any]:
        """
        Extract company rules from Company_Handbook.md with error handling.

        Returns:
            Dictionary of company rules
        """
        try:
            if self.company_handbook_path.exists():
                content = self.company_handbook_path.read_text()
                # This is a simplified implementation - in a full implementation
                # we would parse the handbook for specific rules
                rules = {
                    'auto_reply_emails': True,
                    'approval_required_for_payments_over': 100,  # dollars
                    'approval_required_for_social_posts': True,
                    'response_time_requirements': '24_hours',
                    'default_priority': 'medium'
                }
                self.logger.info("Company rules loaded successfully")
                return rules
            else:
                self.logger.warning("Company handbook not found, using default rules")
                return {}
        except Exception as e:
            self.logger.error(f"Error reading company handbook: {e}", exc_info=True)
            return {}

    def process_needs_action_file(self, file_path: Path) -> bool:
        """
        Process a single file from Needs_Action and create a Plan.md with error handling.

        Args:
            file_path: Path to the file to process

        Returns:
            Boolean indicating success
        """
        try:
            self.logger.info(f"Processing file: {file_path.name}")
            content = file_path.read_text()

            # Determine the type of action needed based on file content
            action_type = self.determine_action_type(content)
            self.logger.debug(f"Determined action type: {action_type}")

            # Create a plan based on the action type
            plan_content = self.create_plan(action_type, content, file_path.stem)

            # Create the plan file
            plan_filename = f"PLAN_{file_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            plan_path = self.plans_path / plan_filename

            plan_path.write_text(plan_content)
            self.logger.info(f"Created plan: {plan_path.name}")

            # Update dashboard with plan creation
            self.update_dashboard(f"Created plan: {plan_filename}")

            # If plan requires approval, create approval request
            requires_approval = self.plan_requires_approval(plan_content)
            self.logger.debug(f"Plan requires approval: {requires_approval}")

            if requires_approval:
                approval_request = self.create_approval_request(plan_content, plan_path)
                if approval_request:
                    self.logger.info(f"Created approval request: {approval_request.name}")
                    return True
            else:
                self.logger.debug("Plan does not require approval")

            return True

        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {e}", exc_info=True)
            return False

    def determine_action_type(self, content: str) -> str:
        """
        Determine the type of action needed based on file content.

        Args:
            content: Content of the file

        Returns:
            Action type string
        """
        content_lower = content.lower()

        # Define action type keywords
        action_keywords = {
            'email_response': ['email', 'gmail', 'message', 'reply', 'respond'],
            'whatsapp_response': ['whatsapp', 'whatsapp message', 'chat'],
            'linkedin_action': ['linkedin', 'opportunity', 'connection', 'network'],
            'payment_processing': ['payment', 'invoice', 'bill', 'money', 'financial', 'transfer'],
            'social_media_action': ['social', 'post', 'tweet', 'facebook', 'instagram', 'media'],
            'task_processing': ['task', 'todo', 'todo list', 'reminder', 'action item'],
            'meeting': ['meeting', 'appointment', 'calendar', 'schedule', 'event'],
            'document': ['document', 'file', 'report', 'contract', 'agreement']
        }

        # Score each action type based on keyword matches
        scores = {}
        for action_type, keywords in action_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            scores[action_type] = score

        # Return the action type with the highest score
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        else:
            return 'general_action'

    def create_plan(self, action_type: str, content: str, source_file: str) -> str:
        """
        Create a structured plan based on action type.

        Args:
            action_type: Type of action to plan for
            content: Original content to base the plan on
            source_file: Name of the source file

        Returns:
            String containing the plan content
        """
        plan_content = f"""---
created: {datetime.now().isoformat()}
source: {source_file}
action_type: {action_type}
status: pending_approval
priority: {self.get_priority_for_type(action_type)}
estimated_completion: {self.get_estimated_completion(action_type)}
---

# Action Plan

## Objective
{self.get_objective_for_action_type(action_type, content)}

## Context
{content[:500] + '...' if len(content) > 500 else content}

## Action Steps
{self.get_action_steps_for_type(action_type)}

## Timeline
- Priority: {self.get_priority_for_type(action_type)}
- Estimated completion: {self.get_estimated_completion(action_type)}

## Resources Needed
- Access to relevant systems
- Any necessary approvals
- Company handbook guidelines

## Success Criteria
- [ ] Action completed according to company handbook rules
- [ ] Proper documentation created
- [ ] Stakeholders notified as required
- [ ] Follow-up actions completed if needed

## Notes
- Follow company handbook guidelines for this type of action
- Ensure all required approvals are obtained before execution
- Document results for future reference
"""

        return plan_content

    def get_objective_for_action_type(self, action_type: str, content: str) -> str:
        """
        Get the objective for a specific action type.

        Args:
            action_type: Type of action
            content: Content to analyze

        Returns:
            Objective string
        """
        objectives = {
            'email_response': 'Respond to email appropriately based on content and sender',
            'whatsapp_response': 'Respond to WhatsApp message following company communication guidelines',
            'linkedin_action': 'Take appropriate action on LinkedIn opportunity or engagement',
            'payment_processing': 'Process payment or invoice according to financial policies',
            'social_media_action': 'Create or manage social media content per brand guidelines',
            'task_processing': 'Complete task with appropriate follow-up and documentation',
            'meeting': 'Prepare for and manage meeting or appointment',
            'document': 'Process, review, or manage document as needed',
            'general_action': 'Handle general action item'
        }

        objective = objectives.get(action_type, 'Handle general action item')

        # Add more specific details if possible
        if 'urgent' in content.lower():
            objective = f"URGENT: {objective}"
        elif 'asap' in content.lower():
            objective = f"ASAP: {objective}"
        elif 'high priority' in content.lower():
            objective = f"HIGH PRIORITY: {objective}"

        return objective

    def get_action_steps_for_type(self, action_type: str) -> str:
        """
        Get the action steps for a specific action type.

        Args:
            action_type: Type of action

        Returns:
            String containing action steps
        """
        steps = {
            'email_response': """- [ ] Review email content and context thoroughly
- [ ] Consult company handbook for response guidelines
- [ ] Identify sender and assess urgency/priority
- [ ] Draft appropriate response following company communication standards
- [ ] Check for approval requirements (based on sender, content, or amount)
- [ ] Proofread and ensure professional tone
- [ ] Send response or create approval request if needed
- [ ] Log correspondence for follow-up tracking""",

            'whatsapp_response': """- [ ] Review message content and sender details
- [ ] Consult company handbook for WhatsApp communication rules
- [ ] Assess urgency and appropriate response time
- [ ] Draft appropriate response following business communication guidelines
- [ ] Apply brand voice and professional standards
- [ ] Send response or escalate if needed based on company policy
- [ ] Document interaction for tracking""",

            'linkedin_action': """- [ ] Review LinkedIn opportunity/content for relevance
- [ ] Assess business value and potential impact
- [ ] Consult social media guidelines and brand standards
- [ ] Take appropriate action (respond, engage, connect, or schedule)
- [ ] Follow up as needed per company guidelines
- [ ] Document outcome and results for tracking
- [ ] Update business development records""",

            'payment_processing': """- [ ] Review payment details and verify accuracy
- [ ] Check recipient information and account details
- [ ] Verify amount and cross-reference with invoice/order
- [ ] Check approval requirements (amount-based thresholds)
- [ ] Process payment through approved channels or create approval request
- [ ] Record transaction with proper documentation
- [ ] Notify relevant parties of completion""",

            'social_media_action': """- [ ] Review content requirements and brand guidelines
- [ ] Ensure content aligns with company messaging
- [ ] Check approval requirements for posting
- [ ] Create engaging content with appropriate hashtags
- [ ] Schedule post at optimal time or prepare for approval
- [ ] Monitor engagement after posting
- [ ] Document results and feedback for improvement""",

            'task_processing': """- [ ] Review task requirements and deliverables
- [ ] Break down into actionable and measurable steps
- [ ] Assign realistic timeline and resources
- [ ] Execute each step with attention to detail
- [ ] Document progress and completion status
- [ ] Communicate results to relevant stakeholders
- [ ] Archive completed tasks for reference""",

            'meeting': """- [ ] Review meeting details and objectives
- [ ] Prepare agenda and required materials
- [ ] Confirm attendance and logistics
- [ ] Set up any required technology
- [ ] Conduct meeting following company protocols
- [ ] Take detailed notes and track decisions
- [ ] Distribute follow-up materials and action items""",

            'document': """- [ ] Review document type and purpose
- [ ] Assess for compliance with company standards
- [ ] Make necessary edits or improvements
- [ ] Ensure proper formatting and presentation
- [ ] Archive document in appropriate location
- [ ] Notify relevant parties if required
- [ ] Track document lifecycle as needed""",

            'general_action': """- [ ] Analyze requirements and constraints
- [ ] Determine most appropriate course of action
- [ ] Follow company guidelines and best practices
- [ ] Execute action with proper documentation
- [ ] Verify completion and results
- [ ] Notify stakeholders as required
- [ ] Archive for future reference"""
        }

        return steps.get(action_type, steps['general_action'])

    def get_priority_for_type(self, action_type: str) -> str:
        """
        Get priority for a specific action type.

        Args:
            action_type: Type of action

        Returns:
            Priority string
        """
        priorities = {
            'email_response': 'Standard',
            'whatsapp_response': 'Standard',
            'linkedin_action': 'Standard',
            'payment_processing': 'High',
            'social_media_action': 'Standard',
            'task_processing': 'Standard',
            'meeting': 'High',
            'document': 'Low',
            'general_action': 'Standard'
        }

        # Use company default if not specified
        return priorities.get(action_type, self.company_rules.get('default_priority', 'Standard'))

    def get_estimated_completion(self, action_type: str) -> str:
        """
        Get estimated completion time for a specific action type.

        Args:
            action_type: Type of action

        Returns:
            Estimated completion time string
        """
        completion_times = {
            'email_response': '1-2 hours',
            'whatsapp_response': '30 minutes',
            'linkedin_action': '2-4 hours',
            'payment_processing': '1 business day',
            'social_media_action': '2-4 hours',
            'task_processing': '2-8 hours',
            'meeting': '1 day (prep) + duration',
            'document': '1-4 hours',
            'general_action': '2-4 hours'
        }

        return completion_times.get(action_type, '2-4 hours')

    def plan_requires_approval(self, plan_content: str) -> bool:
        """
        Determine if the plan requires approval based on content.

        Args:
            plan_content: Content of the plan

        Returns:
            Boolean indicating if approval is required
        """
        # In a more sophisticated implementation, this would check the company rules
        # against the specific plan content
        content_lower = plan_content.lower()

        # Check for payment-related keywords
        payment_keywords = ['payment', 'invoice', 'bill', 'money', 'financial', 'transfer', 'amount over']
        for keyword in payment_keywords:
            if keyword in content_lower:
                # Check if amount exceeds threshold
                amount = self.extract_amount(plan_content)
                threshold = self.company_rules.get('approval_required_for_payments_over', 100)
                if amount > threshold:
                    self.logger.debug(f"Payment amount {amount} exceeds threshold {threshold}, requires approval")
                    return True
                # Even small payments require approval as per company rule
                return True

        # Check for social media posting
        social_keywords = ['post', 'social', 'linkedin', 'tweet', 'facebook', 'instagram', 'share']
        for keyword in social_keywords:
            if keyword in content_lower and 'approval' not in content_lower:
                # Check company rule for social media approval
                if self.company_rules.get('approval_required_for_social_posts', True):
                    self.logger.debug("Social media action requires approval")
                    return True

        # Check for other sensitive actions
        sensitive_keywords = ['contract', 'agreement', 'legal', 'hire', 'fire', 'employee', 'salary', 'compensation']
        for keyword in sensitive_keywords:
            if keyword in content_lower:
                self.logger.debug(f"Sensitive action '{keyword}' requires approval")
                return True

        return False

    def create_approval_request(self, plan_content: str, plan_path: Path) -> Optional[Path]:
        """
        Create an approval request file with enhanced details.

        Args:
            plan_content: Content of the plan
            plan_path: Path to the plan file

        Returns:
            Path to the approval request file or None if creation failed
        """
        try:
            # Extract type and details from plan
            if 'payment' in plan_content.lower() or 'invoice' in plan_content.lower():
                action_type = 'payment_approval'
                amount = self.extract_amount(plan_content)
            elif 'post' in plan_content.lower() or 'linkedin' in plan_content.lower() or 'social' in plan_content.lower():
                action_type = 'social_media_approval'
                amount = 0  # No monetary amount for social media
            elif 'contract' in plan_content.lower() or 'agreement' in plan_content.lower():
                action_type = 'contract_approval'
                amount = 0
            else:
                action_type = 'general_approval'
                amount = 0

            approval_content = f"""---
type: approval_request
action: {action_type}
amount: {amount}
plan_file: {plan_path.name}
created: {datetime.now().isoformat()}
expires: {datetime.now().replace(day=datetime.now().day+1).isoformat()}  # Expires in 1 day
status: pending
priority: high
---

## Approval Request

### Plan Details
- Plan file: {plan_path.name}
- Action type: {action_type}
- Amount (if applicable): ${amount:.2f}
- Created: {datetime.now().isoformat()}

### Request Summary
This action requires your approval before execution. Please review the plan and either approve or reject.

### Plan Content Preview
{plan_content[:300] + '...' if len(plan_content) > 300 else plan_content}

### Approval Options
- **APPROVE**: Move this file to the /Approved folder
- **REJECT**: Move this file to the /Rejected folder with a reason in a comment

### Business Impact
- This action may affect business operations
- Please consider the implications before approving
- Refer to company handbook if uncertain

## Action Required
Your approval is required to proceed with this action. Please review and respond within 24 hours.
"""

            # Create approval file
            approval_filename = f"APPROVAL_{plan_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            approval_path = self.pending_approval_path / approval_filename

            approval_path.write_text(approval_content)
            self.logger.info(f"Approval request created at: {approval_path}")
            return approval_path

        except Exception as e:
            self.logger.error(f"Error creating approval request: {e}", exc_info=True)
            return None

    def extract_amount(self, content: str) -> float:
        """
        Extract amount from content (improved implementation).

        Args:
            content: Text to extract amount from

        Returns:
            Extracted amount as float, or 0.0 if not found
        """
        # Look for patterns like $XXX.XX, XXX.XX USD, etc.
        amount_patterns = [
            r'\$\s*(\d+(?:\.\d{2})?)',  # $XX.XX
            r'(\d+(?:\.\d{2})?)\s*dollars?',  # XX dollars
            r'(\d+(?:\.\d{2})?)\s*USD',  # XX USD
            r'(\d+(?:\.\d{2})?)\s*EUR',  # XX EUR
            r'(\d+(?:\.\d{2})?)\s*GBP',  # XX GBP
            r'(\d+(?:\.\d{2})?)\s*[Ee]uro?s?',  # XX Euro
        ]

        for pattern in amount_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                try:
                    amount = float(match)
                    self.logger.debug(f"Extracted amount: {amount}")
                    return amount
                except ValueError:
                    continue
        return 0.0

    def update_dashboard(self, message: str):
        """
        Update the Dashboard.md file with a new message.

        Args:
            message: Message to add to the dashboard
        """
        try:
            dashboard_content = ""
            if self.dashboard_path.exists():
                dashboard_content = self.dashboard_path.read_text()

            # Add the new message
            new_entry = f"\n- {datetime.now().strftime('%Y-%m-%d %H:%M')} - {message}"
            updated_content = dashboard_content + new_entry

            self.dashboard_path.write_text(updated_content)
            self.logger.debug(f"Dashboard updated with: {message}")
        except Exception as e:
            self.logger.error(f"Error updating dashboard: {e}", exc_info=True)

    def run(self):
        """
        Run the reasoning loop continuously with enhanced error handling.
        """
        self.logger.info("Starting Claude Reasoning Loop...")
        self.logger.info(f"Monitoring: {self.needs_action_path}")

        while True:
            try:
                # Look for files in Needs_Action folder
                needs_action_files = list(self.needs_action_path.glob('*.md'))

                if needs_action_files:
                    self.logger.info(f"Found {len(needs_action_files)} files to process")

                    for file_path in needs_action_files:
                        self.logger.debug(f"Processing: {file_path.name}")
                        success = self.process_needs_action_file(file_path)

                        if success:
                            # Move the processed file to Done folder after creating plan
                            done_path = self.vault_path / 'Done'
                            done_path.mkdir(exist_ok=True)
                            new_file_path = done_path / file_path.name
                            file_path.rename(new_file_path)
                            self.logger.info(f"Moved {file_path.name} to Done folder")
                        else:
                            # If processing failed, move to Error folder for manual review
                            error_path = self.vault_path / 'Error'
                            error_path.mkdir(exist_ok=True)
                            error_file_path = error_path / file_path.name
                            file_path.rename(error_file_path)
                            self.logger.error(f"Moved {file_path.name} to Error folder due to processing failure")
                else:
                    self.logger.debug("No files to process")

                # Wait before checking again
                time.sleep(10)  # Check every 10 seconds

            except KeyboardInterrupt:
                self.logger.info("Reasoning Loop stopped by user.")
                break
            except Exception as e:
                self.logger.error(f"Critical error in reasoning loop: {e}", exc_info=True)
                time.sleep(30)  # Wait longer before retrying on error


def main():
    """Main function to start the reasoning loop."""
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = "."

    try:
        reasoning_loop = ReasoningLoop(vault_path)
        reasoning_loop.run()
    except Exception as e:
        logging.error(f"Failed to start reasoning loop: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()