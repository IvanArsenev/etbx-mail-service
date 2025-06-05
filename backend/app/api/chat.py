"""Chat and email endpoints for sending, receiving, and organizing messages."""

import re
from datetime import datetime
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse

from app.api.deps import get_current_user
from app.core.security import decrypt_password
from app.services import email_service
from app.services.file_service import delete_file

from app.db.models import User
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/chat", tags=["Chat"])


class MessageRequest(BaseModel):
    """Schema for sending a message."""
    receiver: str
    theme: str
    body: str


@router.get("/messages/{folder}")
def get_messages(folder: str, current_user: User = Depends(get_current_user)) -> dict:
    """
    Fetch email messages from a folder.

    Args:
        folder (str): Folder name (e.g. 'inbox', 'Sent', 'noread').

    Returns:
        dict: List of messages.
    """
    password = decrypt_password(current_user.password)
    domain = current_user.mail.split("@")[1]
    imap = "imap.mail.ru" if domain != "pmc-python.ru" else "mail.pmc-python.ru"
    search = "UNSEEN" if folder == "noread" else "ALL"
    emails = email_service.login_and_fetch_emails(current_user.mail, password, folder, search, imap)

    if emails == "Error":
        raise HTTPException(status_code=401, detail="Invalid token or credentials.")

    return {"messages": emails}


@router.post("/send")
def send_message(message: MessageRequest, current_user: User = Depends(get_current_user)) -> dict:
    """
    Send an email message.

    Args:
        message (MessageRequest): Message details.

    Returns:
        dict: Result message.
    """
    password = decrypt_password(current_user.password)
    smtp = "imap.mail.ru" if current_user.mail.split("@")[1] != "pmc-python.ru" else "mail.pmc-python.ru"
    success = email_service.send_email(current_user.mail, password, message.receiver, message.theme, message.body, smtp)

    if success:
        return {"message": "Message sent successfully."}
    return {"message": "Failed to send message. Invalid token or credentials."}


@router.get("/participants")
def get_unique_participants(current_user: User = Depends(get_current_user)) -> dict:
    """
    Get a list of unique email addresses from inbox and sent folders.

    Returns:
        dict: List of participants.
    """
    password = decrypt_password(current_user.password)
    imap = "imap.mail.ru" if current_user.mail.split("@")[1] != "pmc-python.ru" else "mail.pmc-python.ru"

    inbox = email_service.login_and_fetch_emails(current_user.mail, password, "inbox", imap_server=imap)
    sent = email_service.login_and_fetch_emails(current_user.mail, password, "Sent", imap_server=imap)
    if inbox == "Error" or sent == "Error":
        raise HTTPException(status_code=401, detail="Failed to fetch participants.")

    participants = set()
    pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    for msg in inbox + sent:
        matches = re.findall(pattern, msg.get("sender", "") + msg.get("recipient", ""))
        participants.update(matches)

    return {"participants": list(participants)}


@router.get("/themes/{interlocutor}")
def get_themes(interlocutor: str, current_user: User = Depends(get_current_user)) -> dict:
    """
    Get list of subjects exchanged with a specific interlocutor.

    Returns:
        dict: Unique subject lines.
    """
    password = decrypt_password(current_user.password)
    imap = "imap.mail.ru" if current_user.mail.split("@")[1] != "pmc-python.ru" else "mail.pmc-python.ru"
    inbox = email_service.login_and_fetch_emails(current_user.mail, password, "inbox", imap_server=imap)
    sent = email_service.login_and_fetch_emails(current_user.mail, password, "Sent", imap_server=imap)

    if inbox == "Error" or sent == "Error":
        raise HTTPException(status_code=401, detail="Failed to fetch emails.")

    subjects = set()
    for msg in inbox:
        if interlocutor in msg["sender"]:
            subjects.add(clean_subject(msg["subject"]))
    for msg in sent:
        if interlocutor in msg["recipient"]:
            subjects.add(clean_subject(msg["subject"]))

    return {"themes": list(subjects)}


@router.get("/messages_by_theme/{interlocutor}/{theme}")
def get_messages_by_theme(interlocutor: str, theme: str, current_user: User = Depends(get_current_user)) -> dict:
    """
    Get messages exchanged with a given interlocutor filtered by subject.

    Returns:
        dict: List of messages.
    """
    password = decrypt_password(current_user.password)
    imap = "imap.mail.ru" if current_user.mail.split("@")[1] != "pmc-python.ru" else "mail.pmc-python.ru"
    inbox = email_service.login_and_fetch_emails(current_user.mail, password, "inbox", imap_server=imap)
    sent = email_service.login_and_fetch_emails(current_user.mail, password, "Sent", imap_server=imap)

    if inbox == "Error" or sent == "Error":
        raise HTTPException(status_code=401, detail="Invalid token.")

    def match_theme(subj: str) -> bool:
        return subj == theme or subj.startswith(f"Re: {theme}")

    messages = [
        msg for msg in inbox if interlocutor in msg["sender"] and match_theme(msg["subject"])
    ] + [
        msg for msg in sent if interlocutor in msg["recipient"] and match_theme(msg["subject"])
    ]

    for msg in messages:
        msg["parsed_time"] = datetime.strptime(msg["received_time"], "%H:%M %d.%m.%Y")

    messages.sort(key=lambda m: m["parsed_time"])
    for msg in messages:
        del msg["parsed_time"]

    return {"messages": messages}


@router.get("/attachments/{folder}/{mail_id}/{file_name}")
def get_attachment(
    folder: str,
    mail_id: str,
    file_name: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
) -> FileResponse:
    """
    Fetch and return a file attachment from an email.

    Returns:
        FileResponse: The attachment file.
    """
    password = decrypt_password(current_user.password)
    imap = "imap.mail.ru" if current_user.mail.split("@")[1] != "pmc-python.ru" else "mail.pmc-python.ru"

    file_path, content_type = email_service.fetch_email_attachment(
        current_user.mail,
        password,
        mail_id,
        file_name,
        folder,
        imap
    )

    if file_path == "Error" or not file_path or not content_type:
        raise HTTPException(status_code=404, detail="Attachment not found.")

    background_tasks.add_task(delete_file, file_path)
    return FileResponse(file_path, media_type=content_type, filename=file_name)


def clean_subject(subject: str) -> str:
    """Remove 'Re: ' prefix from subject lines."""
    return subject[4:] if subject.lower().startswith("re: ") else subject
