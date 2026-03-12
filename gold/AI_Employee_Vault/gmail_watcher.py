# gmail_watcher.py
import time
import logging
from pathlib import Path
from base_watcher import BaseWatcher
from datetime import datetime
import json
import base64
import email
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']

class GmailWatcher(BaseWatcher):
    def __init__(self, vault_path: str, credentials_path: str = None, token_path: str = "token.json"):
        super().__init__(vault_path, check_interval=120)  # Check every 2 minutes
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self.processed_ids = set()
        self.setup_gmail_service()

    def setup_gmail_service(self):
        """Set up the Gmail API service"""
        creds = None

        # The file token.json stores the user's access and refresh tokens.
        if Path(self.token_path).exists():
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logging.error(f"Could not refresh credentials: {e}")
                    # Delete the token file and get new credentials
                    if Path(self.token_path).exists():
                        Path(self.token_path).unlink()
                    creds = None

            if not creds:
                if not self.credentials_path or not Path(self.credentials_path).exists():
                    # Create a dummy service that will indicate that authentication is needed
                    self.logger.error("Gmail credentials not found. Please follow the setup instructions in the README.")
                    return
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        self.service = build('gmail', 'v1', credentials=creds)

    def check_for_updates(self) -> list:
        """Check Gmail for new emails and return list of new messages"""
        if not self.service:
            self.logger.error("Gmail service not initialized")
            return []

        try:
            # Get messages with 'is:unread is:important' or all unread
            results = self.service.users().messages().list(
                userId='me', q='is:unread'
            ).execute()
            messages = results.get('messages', [])

            # Filter for truly new messages (not already processed)
            new_messages = []
            for msg in messages:
                if msg['id'] not in self.processed_ids:
                    try:
                        full_msg = self.service.users().messages().get(
                            userId='me', id=msg['id']
                        ).execute()

                        # Mark as read to avoid processing again
                        self.service.users().messages().modify(
                            userId='me',
                            id=msg['id'],
                            body={'removeLabelIds': ['UNREAD']}
                        ).execute()

                        new_messages.append(full_msg)
                        self.processed_ids.add(msg['id'])
                    except Exception as e:
                        self.logger.error(f"Error fetching message {msg['id']}: {e}")

            return new_messages
        except HttpError as error:
            self.logger.error(f"An error occurred: {error}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error checking for updates: {e}")
            return []

    def create_action_file(self, message) -> Path:
        """Create markdown file in Needs_Action folder for the email"""
        if not message or 'payload' not in message:
            self.logger.error("Invalid message format")
            return None

        try:
            # Extract headers
            headers = {h['name']: h['value'] for h in message['payload'].get('headers', [])}

            # Extract subject and sender
            subject = headers.get('Subject', 'No Subject')
            sender = headers.get('From', 'Unknown Sender')
            date = headers.get('Date', datetime.now().isoformat())

            # Extract email body
            body = self.extract_email_body(message)

            # Determine priority based on sender or subject
            priority = 'medium'
            if 'urgent' in subject.lower() or 'asap' in subject.lower() or 'important' in subject.lower():
                priority = 'high'
            elif sender and any(keyword in sender.lower() for keyword in ['client', 'boss', 'manager']):
                priority = 'high'

            content = f'''---
type: email
from: {sender}
subject: {subject}
received: {date}
priority: {priority}
status: pending
---

## Email Content
{body}

## Suggested Actions
- [ ] Review content
- [ ] Reply if necessary
- [ ] Forward to relevant party if needed
- [ ] Archive after processing

## Metadata
- Thread ID: {message.get('threadId', 'N/A')}
- Message ID: {message.get('id', 'N/A')}
'''

            # Sanitize filename
            safe_subject = "".join(c for c in subject if c.isalnum() or c in (' ', '-', '_')).rstrip()
            if len(safe_subject) > 50:
                safe_subject = safe_subject[:50]

            filepath = self.needs_action / f'EMAIL_{safe_subject}_{message["id"][:8]}.md'
            filepath.write_text(content)

            self.logger.info(f'Created action file: {filepath.name}')
            return filepath
        except Exception as e:
            self.logger.error(f"Error creating action file for message: {e}")
            return None

    def extract_email_body(self, message):
        """Extract email body from message"""
        try:
            payload = message['payload']
            if 'body' in payload:
                if 'data' in payload['body']:
                    body_data = payload['body']['data']
                    body_decoded = base64.urlsafe_b64decode(body_data.encode('ASCII')).decode('UTF-8')
                    return body_decoded

            # For multipart messages
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        body_data = part['body']['data']
                        body_decoded = base64.urlsafe_b64decode(body_data.encode('ASCII')).decode('UTF-8')
                        return body_decoded
                    elif part['mimeType'] == 'text/html':
                        body_data = part['body']['data']
                        body_decoded = base64.urlsafe_b64decode(body_data.encode('ASCII')).decode('UTF-8')
                        # Convert simple HTML to plain text
                        import re
                        clean = re.compile('<.*?>')
                        return re.sub(clean, '', body_decoded)

            return "Could not extract email body"
        except Exception as e:
            self.logger.error(f"Error extracting email body: {e}")
            return "Error extracting email body"

    def run(self):
        """Main run loop for the watcher"""
        self.logger.info(f'Starting {self.__class__.__name__}')

        if not self.service:
            self.logger.error("Gmail service not initialized. Please authenticate first.")
            return

        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    self.create_action_file(item)
            except Exception as e:
                self.logger.error(f'Error in {self.__class__.__name__}: {e}')
            time.sleep(self.check_interval)

def main():
    import sys
    vault_path = sys.argv[1] if len(sys.argv) > 1 else "."
    credentials_path = sys.argv[2] if len(sys.argv) > 2 else "credentials.json"

    watcher = GmailWatcher(vault_path, credentials_path)
    watcher.run()

if __name__ == "__main__":
    main()