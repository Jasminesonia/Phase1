from typing import List
from fastapi import HTTPException
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jinja2 import Environment, select_autoescape, PackageLoader
from pydantic import EmailStr
from starlette import status
from config import settings

env = Environment(
    loader=PackageLoader("templates", ""),
    autoescape=select_autoescape(["html"]),
)


class VerifyEmail:
    # print("enter VerifyEmail")

    def __init__(self, name: str, code: int, email: List[str]):
        self.name = name
        self.email = email
        self.code = code

    async def sendMail(self, subject, template):
        try:
            print("enter VerifyEmail")
            # Define the emailsetup config
            conf = ConnectionConfig(
                MAIL_USERNAME=settings.EMAIL_USERNAME,
                MAIL_PASSWORD=settings.EMAIL_PASSWORD,
                MAIL_FROM=settings.EMAIL_FROM,
                MAIL_PORT=settings.EMAIL_PORT,
                MAIL_SERVER=settings.EMAIL_HOST,
                MAIL_FROM_NAME=settings.EMAIL_FROM_NAME,
                MAIL_TLS=True,
                MAIL_SSL=False,
            )
            # Generate the HTML templates
            template = env.get_template(f"{template}.html")
            html = template.render(code=self.code, first_name=self.name, subject=subject)

            # Define the message options
            message = MessageSchema(
                subject=subject, recipients=self.email, body=html, subtype="html",
            )

            # Send the emailsetup
            fm = FastMail(conf)
            await fm.send_message(message)
            print("Email sent successfully!")

        except Exception as e:
            print(f"Failed to send emailsetup: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification emailsetup."
            )

    async def sendVerificationCode(self):
        print("enter VerifyEmail")
        await self.sendMail("Welcome to Shopana.ai! Please Verify Your Email", "verification")


class ForgotPassEmail:
    print('enter ForgotPassEmail from auth')

    def __init__(self, name: str, code: str, email: List[EmailStr]):
        self.name = name
        self.email = email
        self.code = code
        pass

    async def sendMail(self, subject, template):
        # Define the config
        print('enter sendMail')
        conf = ConnectionConfig(
            MAIL_USERNAME=settings.EMAIL_USERNAME,
            MAIL_PASSWORD=settings.EMAIL_PASSWORD,
            MAIL_FROM=settings.EMAIL_FROM,
            MAIL_PORT=settings.EMAIL_PORT,
            MAIL_SERVER=settings.EMAIL_HOST,
            MAIL_FROM_NAME=settings.EMAIL_FROM_NAME,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
        )
        # Generate the HTML templates base on the templates name
        template = env.get_template(f"{template}.html")

        html = template.render(code=self.code, first_name=self.name, subject=subject)

        # Define the message options
        message = MessageSchema(
            subject=subject, recipients=self.email, body=html, subtype="html"
        )

        # Send the emailsetup
        fm = FastMail(conf)
        await fm.send_message(message)
        print('enter ForgotPassEmail')

    async def sendVerificationCode(self):
        print('enter sendVerificationCode')
        await self.sendMail("Password Reset Confirmation", "forgotPass")
