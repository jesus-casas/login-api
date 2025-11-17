from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr

conf = ConnectionConfig(
    MAIL_USERNAME="",
    MAIL_PASSWORD="",
    MAIL_FROM="",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

async def send_email(subject: str, email_to: EmailStr, body: str):
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=body,
        subtype="html"  # or "plain"
    )

    fm = FastMail(conf)
    await fm.send_message(message)