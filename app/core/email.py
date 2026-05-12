import html

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings
import html


conf = ConnectionConfig(
    MAIL_USERNAME = settings.MAIL_USERNAME,
    MAIL_PASSWORD = settings.MAIL_PASSWORD,
    MAIL_FROM = settings.MAIL_FROM,
    MAIL_PORT=587,
    MAIL_SERVER= settings.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

mail = FastMail(conf)

async def send_order_confirmation_email(email_to:str, order_id:str, total:float):
    html - f""" 
    <h1>Order Confirmed!</h1>
    <p>Thank you for your purchase.</p>
    <p>Order ID: <strong>{order_id}</strong></p>
    <p>Total: <strong>BDT {total:.2f}</strong></p>
      """
    
    message = MessageSchema(
        subject = "Your Order Confirmation",
        recipients = [email_to],
        html = html,
        subtype= "html"
    )

    #Fire and forget - background task will handle the sending
    await mail.send_message(message)