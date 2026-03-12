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

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('reasoning_loop.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ReasoningLoop:
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

    def get_company_rules(self) -> dict:
        """Extract company rules from Company_Handbook.md"""
        try:
            if self.company_handbook_path.exists():
                content = self.company_handbook_path.read_text()
                # This is a simplified implementation - in a full implementation
                # we would parse the handbook for specific rules
                rules = {
                    'auto_reply_emails': True,
                    'approval_required_for_payments_over': 100,  # dollars
                    'approval_required_for_social_posts': True,
                    'response_time_requirements': '24_hours'
                }
                return rules
            else:
                return {}
        except Exception as e:
            logger.error(f"Error reading company handbook: {e}")
            return {}

    def process_needs_action_file(self, file_path: Path) -> bool:
        """Process a single file from Needs_Action and create a Plan.md"""
        try:
            logger.info(f"Processing file: {file_path.name}")
            content = file_path.read_text()

            # Determine the type of action needed based on file content
            action_type = self.determine_action_type(content)

            # Create a plan based on the action type
            plan_content = self.create_plan(action_type, content, file_path.stem)

            # Create the plan file
            plan_filename = f"PLAN_{file_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            plan_path = self.plans_path / plan_filename

            plan_path.write_text(plan_content)
            logger.info(f"Created plan: {plan_path.name}")

            # Update dashboard with plan creation
            self.update_dashboard(f"Created plan: {plan_filename}")

            # If plan requires approval, create approval request
            if self.plan_requires_approval(plan_content):
                approval_request = self.create_approval_request(plan_content, plan_path)
                if approval_request:
                    logger.info(f"Created approval request: {approval_request.name}")

            return True

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return False

    def determine_action_type(self, content: str) -> str:
        """Determine the type of action needed based on file content"""
        content_lower = content.lower()

        if 'email' in content_lower or 'gmail' in content_lower:
            return 'email_response'
        elif 'whatsapp' in content_lower or 'message' in content_lower:
            return 'whatsapp_response'
        elif 'linkedin' in content_lower or 'opportunity' in content_lower:
            return 'linkedin_action'
        elif 'payment' in content_lower or 'invoice' in content_lower or 'bill' in content_lower:
            return 'payment_processing'
        elif 'social' in content_lower or 'post' in content_lower:
            return 'social_media_action'
        elif 'task' in content_lower or 'todo' in content_lower:
            return 'task_processing'
        else:
            return 'general_action'

    def create_plan(self, action_type: str, content: str, source_file: str) -> str:
        """Create a structured plan based on action type"""
        plan_content = f"""---
created: {datetime.now().isoformat()}
source: {source_file}
action_type: {action_type}
status: pending_approval
priority: medium
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

## Success Criteria
- [ ] Action completed according to company handbook rules
- [ ] Proper documentation created
- [ ] Stakeholders notified as required

## Notes
- Follow company handbook guidelines for this type of action
- Ensure all required approvals are obtained before execution
"""

        return plan_content

    def get_objective_for_action_type(self, action_type: str, content: str) -> str:
        """Get the objective for a specific action type"""
        objectives = {
            'email_response': 'Respond to email appropriately based on content and sender',
            'whatsapp_response': 'Respond to WhatsApp message following company communication guidelines',
            'linkedin_action': 'Take appropriate action on LinkedIn opportunity or engagement',
            'payment_processing': 'Process payment or invoice according to financial policies',
            'social_media_action': 'Create or manage social media content per brand guidelines',
            'task_processing': 'Complete task with appropriate follow-up and documentation',
            'general_action': 'Take appropriate action based on the information provided'
        }

        objective = objectives.get(action_type, 'Handle general action item')

        # Add more specific details if possible
        if 'urgent' in content.lower():
            objective = f"URGENT: {objective}"
        elif 'asap' in content.lower():
            objective = f"ASAP: {objective}"

        return objective

    def get_action_steps_for_type(self, action_type: str) -> str:
        """Get the action steps for a specific action type"""
        steps = {
            'email_response': """- [ ] Review email content and context
- [ ] Consult company handbook for response guidelines
- [ ] Draft appropriate response
- [ ] Check for approval requirements (based on sender, content, or amount)
- [ ] Send response or create approval request""",

            'whatsapp_response': """- [ ] Review message content and sender
- [ ] Consult company handbook for WhatsApp communication rules
- [ ] Draft appropriate response
- [ ] Apply business communication guidelines
- [ ] Send response or escalate if needed""",

            'linkedin_action': """- [ ] Review LinkedIn opportunity/content
- [ ] Assess business relevance
- [ ] Consult social media guidelines
- [ ] Take appropriate action (respond, engage, or schedule)
- [ ] Document outcome""",

            'payment_processing': """- [ ] Review payment details
- [ ] Verify amount and recipient
- [ ] Check approval requirements (amount-based thresholds)
- [ ] Process payment or create approval request
- [ ] Record transaction""",

            'social_media_action': """- [ ] Review content requirements
- [ ] Follow brand guidelines
- [ ] Check approval requirements
- [ ] Create/post content
- [ ] Monitor engagement""",

            'task_processing': """- [ ] Review task requirements
- [ ] Break down into actionable steps
- [ ] Assign timeline
- [ ] Execute steps
- [ ] Document completion""",

            'general_action': """- [ ] Analyze requirements
- [ ] Determine appropriate action
- [ ] Follow company guidelines
- [ ] Execute action
- [ ] Document results"""
        }

        return steps.get(action_type, steps['general_action'])

    def get_priority_for_type(self, action_type: str) -> str:
        """Get priority for a specific action type"""
        priorities = {
            'email_response': 'Standard',
            'whatsapp_response': 'Standard',
            'linkedin_action': 'Standard',
            'payment_processing': 'High',
            'social_media_action': 'Standard',
            'task_processing': 'Standard',
            'general_action': 'Standard'
        }

        return priorities.get(action_type, 'Standard')

    def get_estimated_completion(self, action_type: str) -> str:
        """Get estimated completion time for a specific action type"""
        completion_times = {
            'email_response': '1-2 hours',
            'whatsapp_response': '30 minutes',
            'linkedin_action': '2-4 hours',
            'payment_processing': '1 business day',
            'social_media_action': '2-4 hours',
            'task_processing': '2-8 hours',
            'general_action': '2-4 hours'
        }

        return completion_times.get(action_type, '2-4 hours')

    def plan_requires_approval(self, plan_content: str) -> bool:
        """Determine if the plan requires approval"""
        # In a more sophisticated implementation, this would check the company rules
        # against the specific plan content
        content_lower = plan_content.lower()

        # Check for payment-related keywords
        payment_keywords = ['payment', 'invoice', 'bill', 'money', 'financial', 'transfer', 'amount over']
        for keyword in payment_keywords:
            if keyword in content_lower:
                return True

        # Check for social media posting
        social_keywords = ['post', 'social', 'linkedin', 'tweet', 'facebook', 'instagram']
        for keyword in social_keywords:
            if keyword in content_lower and 'approval' not in content_lower:
                return True

        return False

    def create_approval_request(self, plan_content: str, plan_path: Path) -> Path:
        """Create an approval request file"""
        try:
            # Extract type and details from plan
            if 'payment' in plan_content.lower():
                action_type = 'payment_approval'
                amount = self.extract_amount(plan_content)
            elif 'post' in plan_content.lower() or 'linkedin' in plan_content.lower():
                action_type = 'social_media_approval'
                amount = 0  # No monetary amount for social media
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
---

## Approval Request

### Plan Details
- Plan file: {plan_path.name}
- Action type: {action_type}

### Request Summary
This action requires your approval before execution. Please review the plan and either approve or reject.

### Plan Content Preview
{plan_content[:300] + '...' if len(plan_content) > 300 else plan_content}

### To Approve
Move this file to the /Approved folder.

### To Reject
Move this file to the /Rejected folder with a reason in a comment.

## Action Required
Your approval is required to proceed with this action.
"""

            # Create approval file
            approval_filename = f"APPROVAL_{plan_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            approval_path = self.pending_approval_path / approval_filename

            approval_path.write_text(approval_content)
            return approval_path

        except Exception as e:
            logger.error(f"Error creating approval request: {e}")
            return None

    def extract_amount(self, content: str) -> float:
        """Extract amount from content (simplified implementation)"""
        import re
        # Look for patterns like $XXX.XX or XXX.XX USD
        amount_patterns = [
            r'\$\s*(\d+(?:\.\d{2})?)',  # $XX.XX
            r'(\d+(?:\.\d{2})?)\s*dollars?',  # XX dollars
            r'(\d+(?:\.\d{2})?)\s*USD',  # XX USD
        ]

        for pattern in amount_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        return 0.0

    def update_dashboard(self, message: str):
        """Update the Dashboard.md file with a new message"""
        try:
            dashboard_content = ""
            if self.dashboard_path.exists():
                dashboard_content = self.dashboard_path.read_text()

            # Add the new message
            new_entry = f"\n- {datetime.now().strftime('%Y-%m-%d %H:%M')} - {message}"
            updated_content = dashboard_content + new_entry

            self.dashboard_path.write_text(updated_content)
        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")

    def run(self):
        """Run the reasoning loop continuously"""
        logger.info("Starting Claude Reasoning Loop...")

        while True:
            try:
                # Look for files in Needs_Action folder
                needs_action_files = list(self.needs_action_path.glob('*.md'))

                if needs_action_files:
                    logger.info(f"Found {len(needs_action_files)} files to process")

                    for file_path in needs_action_files:
                        success = self.process_needs_action_file(file_path)

                        if success:
                            # Move the processed file to Done folder after creating plan
                            done_path = self.vault_path / 'Done'
                            done_path.mkdir(exist_ok=True)
                            new_file_path = done_path / file_path.name
                            file_path.rename(new_file_path)
                            logger.info(f"Moved {file_path.name} to Done folder")

                # Wait before checking again
                time.sleep(10)  # Check every 10 seconds

            except KeyboardInterrupt:
                logger.info("Reasoning Loop stopped by user.")
                break
            except Exception as e:
                logger.error(f"Error in reasoning loop: {e}")
                time.sleep(30)  # Wait longer before retrying on error

def main():
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = "."

    reasoning_loop = ReasoningLoop(vault_path)
    reasoning_loop.run()

if __name__ == "__main__":
    main()