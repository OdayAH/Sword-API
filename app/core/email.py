from __future__ import annotations

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import (
    MAILTRAP_HOST,
    MAILTRAP_PORT,
    MAILTRAP_USERNAME,
    MAILTRAP_PASSWORD,
    MAIL_FROM,
)


def send_email(to: str, subject: str, body: str, sender: str = MAIL_FROM) -> None:
    """Send a plain-text email via Mailtrap SMTP."""
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(MAILTRAP_HOST, MAILTRAP_PORT) as server:
        server.starttls()
        server.login(MAILTRAP_USERNAME, MAILTRAP_PASSWORD)
        server.sendmail(sender, to, msg.as_string())
