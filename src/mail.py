import smtplib
from email.message import EmailMessage

import structlog


logger = structlog.get_logger()


def send_email(
    from_address: str, from_password: str, to_address: str, subject: str, body: str
):
    logger.info(f"Sending email (to={to_address}, subject={subject})")

    email_message = EmailMessage()
    email_message["Subject"] = subject
    email_message["From"] = from_address
    email_message["To"] = to_address
    email_message.set_content(body)

    with smtplib.SMTP_SSL(host="smtp.gmail.com", port=465) as mail_session:
        mail_session.login(from_address, from_password)
        mail_session.send_message(msg=email_message)
        logger.info("Email sent 📨")
