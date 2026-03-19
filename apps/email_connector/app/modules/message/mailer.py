from email.message import EmailMessage
from typing import Self

import aiosmtplib

from app.settings import EmailSettings


class Mailer:
    def __init__(self: Self, *, settings: EmailSettings) -> None:
        self.settings = settings

    async def send(self: Self, message: str, subject: str, recepient: str) -> None:
        mail = EmailMessage()
        mail.set_content(message)
        mail["Subject"] = subject
        mail["To"] = recepient
        mail["From"] = self.settings.user

        await aiosmtplib.send(
            mail,
            hostname=self.settings.smtp_host,
            port=self.settings.smtp_port,
            username=self.settings.user,
            password=self.settings.password,
            use_tls=self.settings.secure,
        )
