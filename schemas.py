from typing import Optional
from pydantic import BaseModel, constr
from datetime import datetime

class GoogleLoginSchema(BaseModel):
    token: str  # Google OAuth ID Token


class SocialMediaRequest(BaseModel):
    user_id: str
    caption: str
    base64_image: str  # Base64-encoded image string


class UserSignupSchema(BaseModel):
    name: str
    email: str
    password: constr(min_length=8)
    passwordConfirm: str
    # created_at: datetime = datetime.now()
    # updated_at: datetime = datetime.now()


class UserSigninSchema(BaseModel):
    email: str
    password: constr(min_length=8)


class ForgotPasswordSchema(BaseModel):
    email: str


class VerifyOTPSchema(BaseModel):
    email: str
    otp: str


class ResetPasswordSchema(BaseModel):
    email: str
    password: constr(min_length=8)
    passwordConfirm: str


class UpdatePasswordSchema(BaseModel):
    email: str
    oldPassword: str
    password: constr(min_length=8)
    passwordConfirm: str


class InstaCredentials(BaseModel):
    user_id: str
    ACCESS_TOKENS: Optional[str]
    IG_USER_ID: Optional[str]


class FacebookCredentials(BaseModel):
    user_id: str
    PAGE_ID: Optional[str]
    FACEBOOK_ACCESS: Optional[str]


class TenantData(BaseModel):
    user_id: str
    insta_credentials: InstaCredentials
    facebook_credentials: FacebookCredentials



