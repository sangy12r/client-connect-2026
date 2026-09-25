"""Email notifications for Client Connect 2026 RSVPs.

Sending is entirely optional. If SMTP settings are missing or the mail server
refuses the connection, send_rsvp_emails() returns a failure reason instead of
raising - the calling code saves the RSVP either way, so a mail problem can
never cost you a response.

Required Streamlit secrets to enable sending:
    ORGANISER_EMAIL = "sangy@example.com"
    SMTP_HOST       = "smtp.office365.com"
    SMTP_PORT       = 587
    SMTP_USERNAME   = "sangy@example.com"
    SMTP_PASSWORD   = "your-app-password"
"""

import smtplib
from email.message import EmailMessage

import streamlit as st


def _secret(key, default=None):
    try:
        value = st.secrets[key]
    except (KeyError, FileNotFoundError):
        return default
    # Strip stray whitespace/newlines - a Gmail App Password pasted with the
    # spaces Google displays it with (or a trailing newline from copy-paste)
    # will otherwise be sent verbatim and get rejected by the mail server.
    if isinstance(value, str):
        return value.strip()
    return value


def get_organiser_email():
    """The organiser address shown on the RSVP page. Safe to call always."""
    return _secret("ORGANISER_EMAIL")


def email_is_configured():
    """True only if every setting needed to actually send is present."""
    return all(
        _secret(key)
        for key in ("ORGANISER_EMAIL", "SMTP_HOST", "SMTP_PORT", "SMTP_USERNAME", "SMTP_PASSWORD")
    )


def _build_client_email(to_address, name, company, response_label, event_details):
    message = EmailMessage()
    message["Subject"] = f"RSVP confirmed - {event_details['name']}"
    message["From"] = _secret("ORGANISER_EMAIL")
    message["To"] = to_address
    message["Reply-To"] = _secret("ORGANISER_EMAIL")
    message.set_content(
        f"Dear {name},\n\n"
        f"Thank you for responding to our invitation.\n\n"
        f"Your response has been recorded as: {response_label}\n\n"
        f"Event details\n"
        f"-------------\n"
        f"Event : {event_details['name']}\n"
        f"Date  : {event_details['date']}\n"
        f"Time  : {event_details['time']}\n"
        f"Venue : {event_details['venue']}\n\n"
        f"Registered against: {to_address} ({company})\n\n"
        f"If you need to change your response, simply open the RSVP link again "
        f"and submit with the same email ID.\n\n"
        f"Warm regards,\n"
        f"Client Connect Team"
    )
    return message


def _build_organiser_email(client_email, name, company, response_label, is_known_client):
    message = EmailMessage()
    flag = "" if is_known_client else "  [NOT ON INVITE LIST]"
    message["Subject"] = f"RSVP{flag}: {name} - {company} - {response_label}"
    message["From"] = _secret("ORGANISER_EMAIL")
    message["To"] = _secret("ORGANISER_EMAIL")
    message["Reply-To"] = client_email

    known_line = (
        "This email was on your imported client list."
        if is_known_client
        else "WARNING: this email was NOT on your imported client list. "
        "Please verify before counting them in the final headcount."
    )

    message.set_content(
        f"New RSVP received.\n\n"
        f"Name     : {name}\n"
        f"Company  : {company}\n"
        f"Email    : {client_email}\n"
        f"Response : {response_label}\n\n"
        f"{known_line}\n"
    )
    return message


def send_rsvp_emails(client_email, name, company, response_label, is_known_client, event_details):
    """Send confirmation to the client and a notification to the organiser.

    Returns (sent: bool, reason: str). Never raises - the caller has already
    saved the RSVP by this point and must not be interrupted by mail problems.
    """
    if not email_is_configured():
        return False, "Email sending is not configured."

    try:
        host = _secret("SMTP_HOST")
        port = int(_secret("SMTP_PORT"))
        username = _secret("SMTP_USERNAME")
        password = _secret("SMTP_PASSWORD")

        client_message = _build_client_email(
            client_email, name, company, response_label, event_details
        )
        organiser_message = _build_organiser_email(
            client_email, name, company, response_label, is_known_client
        )

        with smtplib.SMTP(host, port, timeout=20) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(client_message)
            server.send_message(organiser_message)

        return True, "Confirmation emails sent."

    except smtplib.SMTPAuthenticationError:
        smtp_host = (_secret("SMTP_HOST") or "").lower()
        if "gmail" in smtp_host:
            hint = (
                "This looks like a Gmail account. Make sure 2-Step Verification is turned "
                "on for it, and that SMTP_PASSWORD is a 16-character App Password from "
                "myaccount.google.com/apppasswords - not the account's normal login password."
            )
        elif "office365" in smtp_host or "outlook" in smtp_host:
            hint = "If this is a Microsoft 365 account, SMTP AUTH is most likely disabled by IT."
        else:
            hint = "Double-check SMTP_USERNAME and SMTP_PASSWORD are correct for this mail server."
        return False, f"Mail server rejected the login. {hint}"
    except smtplib.SMTPException as exc:
        return False, f"Mail server error: {exc}"
    except Exception as exc:
        return False, f"Could not send email: {exc}"
