from pydantic import BaseModel

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    patronymic: str | None
    email: str
    password: str
    password_repeat: str
