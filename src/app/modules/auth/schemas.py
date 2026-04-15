from pydantic import BaseModel, ConfigDict


class TokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    access_token: str
    access_token_expire: int
    refresh_token: str
    refresh_token_expire: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str
