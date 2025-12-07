"""
Email MCP Server using FastMCP
This server provides email sending functionality through MCP protocol.
"""

from fastmcp import FastMCP
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from typing import Optional
import json
from dotenv import load_dotenv

# Load environment variables from .env file if present: pip install python-dotenv
load_dotenv()

EMAIL_FROM=os.getenv("EMAIL_FROM")
SMTP_SERVER=os.getenv("SMTP_SERVER")
SMTP_PORT=int(os.getenv("SMTP_PORT"))
SMTP_USERNAME=os.getenv("SMTP_USERNAME")
SMTP_PASSWORD=os.getenv("SMTP_PASSWORD")

# Initialize FastMCP server
mcp = FastMCP("Email Server")


@mcp.tool()
def send_email(
    to_email: str,
    subject: str,
    body: str,
    use_tls: bool = True,
    body_type: str = "plain"
) -> str:
    """
    Send an email through SMTP server.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body content
        use_tls: Whether to use TLS encryption
        body_type: Email body type - 'plain' or 'html'
    
    Returns:
        Success message or error description
    """
    try:
        # Get credentials from environment variables if not provided
        from_email = EMAIL_FROM or os.getenv("EMAIL_FROM")
        smtp_server = SMTP_SERVER or os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = SMTP_PORT or int(os.getenv("SMTP_PORT", 587))
        username = SMTP_USERNAME or os.getenv("SMTP_USERNAME")
        password = SMTP_PASSWORD or os.getenv("SMTP_PASSWORD")

        if not all([from_email, smtp_server, username, password]):
            return "Error: Missing required email configuration. Please provide credentials or set environment variables."
        
        # Create message
        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Subject"] = subject
        
        # Attach body
        msg.attach(MIMEText(body, body_type))
        
        # Connect to SMTP server and send
        server = smtplib.SMTP(smtp_server, smtp_port)
        
        if use_tls:
            server.starttls()
        
        server.login(username, password)
        server.send_message(msg)
        server.quit()
        
        return f"Email sent successfully to {to_email}"
        
    except Exception as e:
        return f"Error sending email: {str(e)}"


@mcp.tool()
def send_email_with_attachment(
    to_email: str,
    subject: str,
    body: str,
    attachment_path: str,
    use_tls: bool = True
) -> str:
    """
    Send an email with an attachment through SMTP server.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body content
        attachment_path: Path to file to attach
        use_tls: Whether to use TLS encryption
    
    Returns:
        Success message or error description
    """
    try:
        # Get credentials from environment variables if not provided
        from_email = EMAIL_FROM or os.getenv("EMAIL_FROM")
        smtp_server = SMTP_SERVER or os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = SMTP_PORT or int(os.getenv("SMTP_PORT", 587))
        username = SMTP_USERNAME or os.getenv("SMTP_USERNAME")
        password = SMTP_PASSWORD or os.getenv("SMTP_PASSWORD")

        if not all([from_email, smtp_server, username, password]):
            return "Error: Missing required email configuration."
        
        # Check if file exists
        if not os.path.exists(attachment_path):
            return f"Error: Attachment file not found: {attachment_path}"
        
        # Create message
        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Subject"] = subject
        
        # Attach body
        msg.attach(MIMEText(body, "plain"))
        
        # Attach file
        filename = os.path.basename(attachment_path)
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )
        msg.attach(part)
        
        # Connect to SMTP server and send
        server = smtplib.SMTP(smtp_server, smtp_port)
        
        if use_tls:
            server.starttls()
        
        server.login(username, password)
        server.send_message(msg)
        server.quit()
        
        return f"Email with attachment sent successfully to {to_email}"
        
    except Exception as e:
        return f"Error sending email with attachment: {str(e)}"


@mcp.tool()
def send_bulk_emails(
    recipients: str,
    subject: str,
    body: str,
    use_tls: bool = True
) -> str:
    """
    Send the same email to multiple recipients.
    
    Args:
        recipients: Comma-separated list of email addresses
        subject: Email subject
        body: Email body content
        use_tls: Whether to use TLS encryption
    
    Returns:
        Summary of sent emails
    """
    try:
        # Parse recipients
        recipient_list = [email.strip() for email in recipients.split(",")]
        
        # Get credentials
        from_email = EMAIL_FROM or os.getenv("EMAIL_FROM")
        smtp_server = SMTP_SERVER or os.getenv("SMTP_SERVER")
        smtp_port = SMTP_PORT or int(os.getenv("SMTP_PORT"))
        username = SMTP_USERNAME or os.getenv("SMTP_USERNAME")
        password = SMTP_PASSWORD or os.getenv("SMTP_PASSWORD")

        if not all([from_email, smtp_server, username, password]):
            return "Error: Missing required email configuration."
        
        # Connect to SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        
        if use_tls:
            server.starttls()
        
        server.login(username, password)
        
        # Send to each recipient
        successful = []
        failed = []
        
        for recipient in recipient_list:
            try:
                msg = MIMEMultipart()
                msg["From"] = from_email
                msg["To"] = recipient
                msg["Subject"] = subject
                msg.attach(MIMEText(body, "plain"))
                
                server.send_message(msg)
                successful.append(recipient)
            except Exception as e:
                failed.append(f"{recipient}: {str(e)}")
        
        server.quit()
        
        result = f"Successfully sent to {len(successful)} recipients."
        if failed:
            result += f"\nFailed for {len(failed)} recipients: {', '.join(failed)}"
        
        return result
        
    except Exception as e:
        return f"Error sending bulk emails: {str(e)}"


if __name__ == "__main__":
    # Run the MCP server
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",  # Use "127.0.0.1" for localhost only, "0.0.0.0" for all interfaces
        port=8085        # Change to your desired port number
    )