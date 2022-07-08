import smtplib
from abc import ABC
from enum import Enum
from pathlib import Path
from typing import Callable
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from dataclasses import dataclass, field


@dataclass
class Attachment:
    filepath: str

    @property
    def filename(self) -> str:
        return Path(self.filepath).name


@dataclass
class SMTPServer:
    address: str
    port: int
    tls: bool

    def to_smtplib(self) -> smtplib.SMTP:
        return smtplib.SMTP(self.address, self.port)


class SMTPServers(ABC):
    OUTLOOK = SMTPServer('smtp-mail.outlook.com', 587, True)
    GMAIL = SMTPServer('smtp.gmail.com', 587, True)


class SendStatus(Enum):
    BUILDING = 0
    CONNECTING = 1
    SENDING = 2
    CLOSING = 3
    DONE = 4


@dataclass
class SendProgress:
    current: int
    total: int
    email: 'Email'
    status: SendStatus


@dataclass
class Email:
    username: str
    password: str
    server: SMTPServer
    sender: str
    recipient: str
    subject: str
    body: str
    attachments: list[Attachment] = field(default_factory=list)

    @staticmethod
    def send_batch(emails: list['Email'], callback: Callable[[SendProgress], None]):
        for i, email in enumerate(emails):
            _callback = lambda status: callback(SendProgress(i + 1, len(emails), email, status))
            email.send(_callback)


    def send(self, callback: Callable[[SendStatus], None]):
        callback(SendStatus.BUILDING)
        message = self._to_mime_multipart().as_string()

        callback(SendStatus.CONNECTING)
        smtp = self.server.to_smtplib()
        if self.server.tls:
            smtp.starttls()
        smtp.login(self.username, self.password)

        callback(SendStatus.SENDING)
        smtp.sendmail(self.sender, self.recipient, message)

        callback(SendStatus.CLOSING)
        smtp.quit()

        callback(SendStatus.DONE)


    def _to_mime_multipart(self) -> MIMEMultipart:
        message = MIMEMultipart()
        message['From'] = self.sender
        message['To'] = self.recipient
        message['Date'] = formatdate(localtime=True)
        message['Subject'] = self.subject
        message.attach(MIMEText(self.body))

        for attachment in self.attachments:
            part = MIMEBase('application', 'octet-stream')
            with open(attachment.filepath, 'rb') as file:
                part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header('content-disposition', 'attachment', filename=attachment.filename)
            message.attach(part)

        return message
    