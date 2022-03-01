import smtplib
from email.message import EmailMessage

import structlog

from classes import SuccessType


logger = structlog.get_logger()


def send_email(
    from_address: str,
    login_address: str,
    login_password: str,
    to_address: str,
    subject: str,
    body: str,
):
    logger.info(f"Sending email (to={to_address}, subject={subject})")

    email_message = EmailMessage()
    email_message["Subject"] = subject
    email_message["From"] = from_address
    email_message["To"] = to_address
    email_message.set_content(body)

    with smtplib.SMTP_SSL(host="smtp.gmail.com", port=465) as mail_session:
        mail_session.login(login_address, login_password)
        mail_session.send_message(msg=email_message)
        logger.info("Email sent 📨")


def get_mail_body_and_subject(repos_test_results):
    subject = "❗ Failing or Untested GitHub Actions Found in Repositories ❗"
    body = "--- ❌ Failed ❌ ---\n"
    body += "\n" + ",\n".join(
        str(rs) for rs in repos_test_results if rs.success_type == SuccessType.FAILED
    )
    body += "\n\n--- ❔ Not Tested ❔ ---\n"
    body += "\n" + ",\n".join(
        str(rs) for rs in repos_test_results if rs.success_type == SuccessType.UNTESTED
    )
    body += "\n\n--- ✅ Success ✅ ---\n"
    body += "\n" + ",\n".join(
        str(rs) for rs in repos_test_results if rs.success_type == SuccessType.PASSED
    )
    return body, subject
