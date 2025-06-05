"""Email service for IMAP/SMTP interactions."""

import os
import re
import imaplib
import email
from datetime import datetime
from typing import List, Optional
from email.header import decode_header
from email.utils import parseaddr, parsedate_tz, mktime_tz
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from bs4 import BeautifulSoup


def send_email(
    sender_email: str,
    password: str,
    receiver_email: str,
    subject: str,
    body: str,
    smtp_server: str = "mail.pmc-python.ru",
    smtp_port: int = 587
) -> bool:
    """
    Send an email using SMTP.

    Returns:
        bool: True if sent, False otherwise.
    """
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, password)
        server.send_message(message)
        server.quit()
        return True
    except Exception:
        return False


def fetch_email_attachment(
    email_user: str,
    password: str,
    mail_id: str,
    filename: str,
    folder: str,
    imap_server: str,
    save_path: str = "files"
) -> tuple[str, str]:
    """
    Fetch an email attachment and save to disk.

    Returns:
        tuple[str, str]: (file path, content type)
    """
    mail = imaplib.IMAP4_SSL(imap_server)
    try:
        mail.login(email_user, password)
    except Exception:
        return "Error", ""

    mail.select(folder)
    _, messages = mail.search(None, "ALL")
    if mail_id.encode() not in messages[0].split():
        mail.logout()
        return "Error", ""

    _, msg_data = mail.fetch(mail_id, "(RFC822)")
    for part in msg_data:
        if isinstance(part, tuple):
            msg = email.message_from_bytes(part[1])
            for subpart in msg.walk():
                if "attachment" in str(subpart.get("Content-Disposition")):
                    fname = decode_header_safe(subpart.get_filename())
                    if fname == filename:
                        os.makedirs(save_path, exist_ok=True)
                        path = os.path.join(save_path, f"{folder}_{mail_id}_{filename}")
                        with open(path, "wb") as f:
                            f.write(subpart.get_payload(decode=True))
                        mail.logout()
                        return path, subpart.get_content_type()

    mail.logout()
    return "Error", ""


def login_and_fetch_emails(
    email_user: str,
    password: str,
    folder: str = "inbox",
    search_filter: str = "ALL",
    imap_server: str = "mail.pmc-python.ru"
) -> List[dict]:
    """
    Log in to an email account and fetch emails.

    Returns:
        List[dict]: List of parsed email data.
    """
    mail = imaplib.IMAP4_SSL(imap_server)
    try:
        mail.login(email_user, password)
    except Exception:
        return "Error"

    try:
        mail.select(folder)
        _, message_ids = mail.search(None, search_filter)
    except Exception:
        return "Error"

    messages = []
    for mail_id in message_ids[0].split():
        _, msg_data = mail.fetch(mail_id, "(RFC822)")
        for part in msg_data:
            if isinstance(part, tuple):
                msg = email.message_from_bytes(part[1])
                messages.append(parse_email_message(mail_id.decode(), msg))

    mail.logout()
    return messages


def parse_email_message(mail_id: str, msg: email.message.Message) -> dict:
    """Parses a raw email message into a dict."""
    subject = decode_header_safe(msg.get("Subject", "None"))
    from_name, from_addr = parseaddr(msg.get("From", ""))
    to_name, to_addr = parseaddr(msg.get("To", ""))
    from_name = decode_header_safe(from_name)
    to_name = decode_header_safe(to_name)

    received = msg.get("Date") or msg.get("Received", "").split(";")[-1].strip()
    date_tuple = parsedate_tz(received)
    formatted_date = datetime.fromtimestamp(mktime_tz(date_tuple)).strftime("%H:%M %d.%m.%Y") if date_tuple else "Unknown"

    body, attachments = extract_body_and_attachments(msg, mail_id)

    return {
        "id": mail_id,
        "subject": subject,
        "body": body.strip(),
        "sender": f"{from_name} <{from_addr}>",
        "recipient": f"{to_name} <{to_addr}>",
        "received_time": formatted_date,
        "files": attachments
    }


def decode_header_safe(value: Optional[str]) -> str:
    """Decode MIME headers safely."""
    if not value:
        return ""
    decoded, encoding = decode_header(value)[0]
    if isinstance(decoded, bytes):
        return decoded.decode(encoding or "utf-8", errors="ignore")
    return decoded


def extract_body_and_attachments(msg: email.message.Message, mail_id: str) -> tuple[str, list[str]]:
    """Extract plain text body and attachment filenames."""
    body = ""
    files = []

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition", ""))

            if "attachment" in disposition:
                fname = decode_header_safe(part.get_filename())
                files.append(f"{mail_id}_{fname}")
            elif content_type in ("text/plain", "text/html"):
                payload = part.get_payload(decode=True)
                if payload:
                    text = payload.decode(errors="ignore")
                    if content_type == "text/html":
                        body += BeautifulSoup(text, "html.parser").get_text()
                    else:
                        body += text
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            body = payload.decode(errors="ignore")
            if msg.get_content_type() == "text/html":
                body = BeautifulSoup(body, "html.parser").get_text()

    return body, files
