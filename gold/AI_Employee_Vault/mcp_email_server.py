#!/usr/bin/env python3
"""
Email MCP (Model Context Protocol) Server
Provides capabilities for sending emails via SMTP
"""

import json
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import asyncio
import sys
from pathlib import Path

class EmailMCPServer:
    def __init__(self):
        self.name = "email-mcp"
        self.version = "1.0.0"
        self.capabilities = {
            "send_email": {
                "description": "Send an email with optional attachments",
                "parameters": {
                    "to": {"type": "string", "description": "Recipient email address"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body content"},
                    "cc": {"type": "string", "description": "CC email address (optional)"},
                    "bcc": {"type": "string", "description": "BCC email address (optional)"},
                    "attachments": {"type": "array", "items": {"type": "string"}, "description": "File paths to attach (optional)"}
                }
            },
            "send_bulk_emails": {
                "description": "Send emails to multiple recipients",
                "parameters": {
                    "recipients": {"type": "array", "items": {"type": "string"}, "description": "List of recipient email addresses"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body content"}
                }
            }
        }

    def get_smtp_config(self):
        """Get SMTP configuration from environment variables"""
        return {
            "server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            "port": int(os.getenv("SMTP_PORT", "587")),
            "username": os.getenv("SMTP_USERNAME"),
            "password": os.getenv("SMTP_PASSWORD"),
            "from_email": os.getenv("SMTP_FROM_EMAIL")
        }

    def send_email(self, to, subject, body, cc=None, bcc=None, attachments=None):
        """Send a single email"""
        try:
            config = self.get_smtp_config()

            if not config["username"] or not config["password"] or not config["from_email"]:
                return {"error": "SMTP credentials not configured in environment variables"}

            # Create message
            msg = MIMEMultipart()
            msg['From'] = config["from_email"]
            msg['To'] = to
            msg['Subject'] = subject

            if cc:
                msg['Cc'] = cc

            # Add body to email
            msg.attach(MIMEText(body, 'plain'))

            # Add attachments if any
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())

                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(file_path)}'
                        )
                        msg.attach(part)

            # Create SMTP session
            server = smtplib.SMTP(config["server"], config["port"])
            server.starttls()  # Enable security
            server.login(config["username"], config["password"])

            # Get all recipients
            all_recipients = [to]
            if cc:
                all_recipients.append(cc)
            if bcc:
                all_recipients.append(bcc)

            # Send email
            text = msg.as_string()
            server.sendmail(config["from_email"], all_recipients, text)
            server.quit()

            return {"success": True, "message": f"Email sent successfully to {to}"}

        except Exception as e:
            return {"error": f"Failed to send email: {str(e)}"}

    def send_bulk_emails(self, recipients, subject, body):
        """Send bulk emails to multiple recipients"""
        results = []
        for recipient in recipients:
            result = self.send_email(recipient, subject, body)
            results.append({
                "recipient": recipient,
                "result": result
            })

        successful = sum(1 for r in results if r["result"].get("success"))
        total = len(recipients)

        return {
            "success": True,
            "summary": f"Sent {successful} out of {total} emails successfully",
            "details": results
        }

    def handle_request(self, request):
        """Handle MCP requests"""
        try:
            request_data = json.loads(request) if isinstance(request, str) else request

            method = request_data.get("method")
            params = request_data.get("params", {})

            if method == "send_email":
                return self.send_email(
                    to=params.get("to"),
                    subject=params.get("subject"),
                    body=params.get("body"),
                    cc=params.get("cc"),
                    bcc=params.get("bcc"),
                    attachments=params.get("attachments")
                )
            elif method == "send_bulk_emails":
                return self.send_bulk_emails(
                    recipients=params.get("recipients", []),
                    subject=params.get("subject"),
                    body=params.get("body")
                )
            else:
                return {"error": f"Unknown method: {method}"}

        except Exception as e:
            return {"error": f"Request handling failed: {str(e)}"}

    def run(self):
        """Run the MCP server"""
        print("Email MCP Server started", file=sys.stderr)
        print(json.dumps({
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "serverInfo": {
                    "name": self.name,
                    "version": self.version
                },
                "capabilities": {
                    "experimental": {
                        "capabilities": self.capabilities
                    }
                }
            },
            "id": 1
        }))

        sys.stdout.flush()

        # Main loop to handle requests
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break

                request = line.strip()
                if not request:
                    continue

                response = self.handle_request(request)

                # Send response
                response_obj = {
                    "jsonrpc": "2.0",
                    "result": response,
                    "id": "response"
                }

                print(json.dumps(response_obj))
                sys.stdout.flush()

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"message": f"Server error: {str(e)}"},
                    "id": "error"
                }))
                sys.stdout.flush()

def main():
    server = EmailMCPServer()
    server.run()

if __name__ == "__main__":
    main()