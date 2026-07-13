import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.enabled = bool(settings.SMTP_HOST and settings.SMTP_USER)

    def send_email(self, to: str, subject: str, html_body: str) -> bool:
        if not self.enabled:
            logger.info("SMTP not configured. Email to %s: %s", to, subject)
            return True

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = settings.SMTP_FROM
            msg["To"] = to
            msg.attach(MIMEText(html_body, "html"))

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.SMTP_FROM, to, msg.as_string())
            return True
        except Exception as e:
            logger.error("Failed to send email: %s", e)
            return False

    def send_verification_email(self, to: str, token: str) -> bool:
        url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        html = f"<p>Verify your email: <a href='{url}'>{url}</a></p>"
        return self.send_email(to, "Verify your SupportAI account", html)

    def send_password_reset_email(self, to: str, token: str) -> bool:
        url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        html = f"<p>Reset your password: <a href='{url}'>{url}</a></p>"
        return self.send_email(to, "Reset your SupportAI password", html)

    def send_invite_email(self, to: str, workspace_name: str, inviter: str) -> bool:
        url = f"{settings.FRONTEND_URL}/signup"
        html = f"<p>{inviter} invited you to join {workspace_name}. <a href='{url}'>Sign up</a></p>"
        return self.send_email(to, f"Invitation to {workspace_name}", html)
