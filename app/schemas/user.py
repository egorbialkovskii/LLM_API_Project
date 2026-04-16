from pydantic import BaseModel, ConfigDict, EmailStr


class UserPublic(BaseModel):
    """Public schema for user responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    role: str
