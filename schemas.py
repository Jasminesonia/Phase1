from pydantic import BaseModel, constr


class SocialMediaRequest(BaseModel):
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



