from pydantic import BaseModel

class User(BaseModel):
    telegram_id: int
    username: str

class LinkData(BaseModel):
    telegram_id: int
    link: str

class Notification(BaseModel):
    user_id: int
    message: str