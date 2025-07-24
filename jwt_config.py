from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from config import settings

class JWTSettings(BaseModel):
    authjwt_secret_key: str = settings.AUTHJWT_SECRET_KEY

@AuthJWT.load_config
def get_jwt_config():
    return JWTSettings()
