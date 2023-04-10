import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import settings
from services.celery.celery_client import app


class EmailTemplate:
    def __init__(self, template_file_path: str):
        with open(template_file_path, "r") as f:
            self.template = f.read()

        css = self.template.split("<style>")[1].split("</style>")[0]
        self.template = self.template.replace(css, "")
        self.css = css

    def format(self, **kwargs) -> str:
        html_body = self.template.format(**kwargs)
        html_body = html_body.replace("<style></style>", "<style>" + self.css + "</style>")
        return html_body


class Email:
    def __init__(self, to: str, subject: str, body: str):
        self.to = to
        self.subject = subject
        self.body = body

    def as_message(self) -> MIMEMultipart:
        message = MIMEMultipart()
        message["From"] = settings.SENDER_MAIL
        message["To"] = self.to
        message["Subject"] = self.subject
        message.attach(MIMEText(self.body, "html"))
        return message


class EmailSender:
    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def send(self, email: Email) -> None:
        smtp_connection = smtplib.SMTP(self.host, self.port)
        smtp_connection.starttls()
        smtp_connection.login(self.username, self.password)
        smtp_connection.sendmail(self.username, email.to, email.as_message().as_string())
        smtp_connection.quit()


class EmailTaskFactory:
    def __init__(self, template_file_path: str, sender: EmailSender):
        self.template = EmailTemplate(template_file_path)
        self.sender = sender


@app.task(queue="email", name="registration_confirmation")
def registration_confirmation(self, site_username: str, confirmation_link: str, to: str) -> None:
    template = EmailTemplate(template_file_path="services/celery/email/template.html")
    sender = EmailSender(
        host=settings.MAIL_HOST,
        port=settings.MAIL_PORT,
        username=settings.SENDER_MAIL,
        password=settings.SENDER_PASSWORD,
    )
    subject = "Registration Confirmation"
    body = template.format(site_username=site_username, confirmation_link=confirmation_link)
    email = Email(to=to, subject=subject, body=body)
    sender.send(email)
