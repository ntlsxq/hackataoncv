import uuid

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    name: str
    id: uuid.UUID
    email: EmailStr

class UserRegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserRegisterResponse(BaseModel):
    user: User
    token: str

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserLoginResponse(BaseModel):
    user: User
    token: str