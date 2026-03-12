#!/usr/bin/env python3
"""
Email MCP (Model Context Protocol) Server
Provides capabilities for sending emails via SMTP with enhanced logging and error handling
"""

import json
import smtplib
import os
import logging
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import Dict, List, Any, Optional


class EmailMCPServer:
    """
    Modular Email MCP Server with enhanced logging and error handling.
    """

    def __init__(self):
        self.name = "email-mcp"
        self.version = "1.0.0"
        self.logger = self._setup_logger()
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

    def _setup_logger(self) -> logging.Logger:
        """Setup logger for the MCP server."""
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)

        # Create file handler
        file_handler = logging.FileHandler('mcp_email_server.log')
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

        # Add handlers to logger
        if not logger.handlers:
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)

        return logger

    def get_smtp_config(self) -> Dict[str, Any]:
        """Get SMTP configuration from environment variables with validation."""
        config = {
            "server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            "port": int(os.getenv("SMTP_PORT", "587")),
            "username": os.getenv("SMTP_USERNAME"),
            "password": os.getenv("SMTP_PASSWORD"),
            "from_email": os.getenv("SMTP_FROM_EMAIL")
        }

        self.logger.debug(f"SMTP Configuration loaded: server={config['server']}, port={config['port']}")
        return config

    def validate_email_address(self, email: str) -> bool:
        """Validate email address format."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def send_email(self, to: str, subject: str, body: str,
                   cc: Optional[str] = None, bcc: Optional[str] = None,
                   attachments: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Send a single email with enhanced validation and error handling.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body content
            cc: CC email address (optional)
            bcc: BCC email address (optional)
            attachments: List of file paths to attach (optional)

        Returns:
            Dict containing success status and message
        """
        try:
            self.logger.info(f"Attempting to send email to: {to}")

            # Validate inputs
            if not self.validate_email_address(to):
                error_msg = f"Invalid recipient email address: {to}"
                self.logger.error(error_msg)
                return {"success": False, "error": error_msg}

            if cc and not self.validate_email_address(cc):
                error_msg = f"Invalid CC email address: {cc}"
                self.logger.error(error_msg)
                return {"success": False, "error": error_msg}

            if bcc and not self.validate_email_address(bcc):
                error_msg = f"Invalid BCC email address: {bcc}"
                self.logger.error(error_msg)
                return {"success": False, "error": error_msg}

            config = self.get_smtp_config()

            if not config["username"] or not config["password"] or not config["from_email"]:
                error_msg = "SMTP credentials not configured in environment variables"
                self.logger.error(error_msg)
                return {"success": False, "error": error_msg}

            # Validate attachment paths
            valid_attachments = []
            if attachments:
                for file_path in attachments:
                    if not os.path.exists(file_path):
                        self.logger.warning(f"Attachment file does not exist: {file_path}")
                    else:
                        valid_attachments.append(file_path)

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
            for file_path in valid_attachments:
                try:
                    with open(file_path, "rb") as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())

                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {os.path.basename(file_path)}'
                    )
                    msg.attach(part)
                    self.logger.debug(f"Added attachment: {file_path}")
                except Exception as e:
                    self.logger.error(f"Failed to attach file {file_path}: {e}")

            # Create SMTP session
            self.logger.debug(f"Connecting to SMTP server: {config['server']}:{config['port']}")
            server = smtplib.SMTP(config["server"], config["port"])
            server.starttls()  # Enable security
            server.login(config["username"], config["password"])
            self.logger.debug("SMTP authentication successful")

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

            self.logger.info(f"Email sent successfully to {to}")
            return {
                "success": True,
                "message": f"Email sent successfully to {to}",
                "timestamp": __import__('time').time()
            }

        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"SMTP authentication failed: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"Failed to send email: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return {"success": False, "error": error_msg}

    def send_bulk_emails(self, recipients: List[str], subject: str, body: str) -> Dict[str, Any]:
        """
        Send bulk emails to multiple recipients with individual error tracking.

        Args:
            recipients: List of recipient email addresses
            subject: Email subject
            body: Email body content

        Returns:
            Dict containing summary and individual results
        """
        self.logger.info(f"Attempting to send bulk emails to {len(recipients)} recipients")

        results = []
        for recipient in recipients:
            try:
                result = self.send_email(recipient, subject, body)
                results.append({
                    "recipient": recipient,
                    "result": result
                })
            except Exception as e:
                self.logger.error(f"Error processing recipient {recipient}: {e}")
                results.append({
                    "recipient": recipient,
                    "result": {"success": False, "error": str(e)}
                })

        successful = sum(1 for r in results if r["result"].get("success"))
        total = len(recipients)

        summary_msg = f"Sent {successful} out of {total} emails successfully"
        self.logger.info(summary_msg)

        return {
            "success": True,
            "summary": summary_msg,
            "details": results,
            "timestamp": __import__('time').time()
        }

    def handle_request(self, request: str) -> Dict[str, Any]:
        """
        Handle MCP requests with enhanced error handling.

        Args:
            request: JSON-RPC request string

        Returns:
            Response dictionary
        """
        try:
            request_data = json.loads(request) if isinstance(request, str) else request

            method = request_data.get("method")
            params = request_data.get("params", {})

            self.logger.debug(f"Handling MCP request: {method}")

            if method == "send_email":
                return self.send_email(
                    to=params.get("to"),
                    subject=params.get("subject", ""),
                    body=params.get("body", ""),
                    cc=params.get("cc"),
                    bcc=params.get("bcc"),
                    attachments=params.get("attachments")
                )
            elif method == "send_bulk_emails":
                return self.send_bulk_emails(
                    recipients=params.get("recipients", []),
                    subject=params.get("subject", ""),
                    body=params.get("body", "")
                )
            else:
                error_msg = f"Unknown method: {method}"
                self.logger.error(error_msg)
                return {"error": error_msg}

        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in request: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Request handling failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return {"error": error_msg}

    def run(self):
        """Run the MCP server with enhanced logging."""
        self.logger.info("Email MCP Server starting...")
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
        }), file=sys.stderr)

        sys.stdout.flush()

        # Main loop to handle requests
        self.logger.info("Email MCP Server initialized and running")
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    self.logger.info("EOF received, shutting down server")
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
                self.logger.info("Received keyboard interrupt, shutting down server")
                break
            except Exception as e:
                self.logger.error(f"Server error: {e}", exc_info=True)
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"message": f"Server error: {str(e)}"},
                    "id": "error"
                }))
                sys.stdout.flush()

def main():
    """Main function to start the MCP server."""
    server = EmailMCPServer()
    server.run()

if __name__ == "__main__":
    main()