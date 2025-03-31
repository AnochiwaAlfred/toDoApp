from ninja import Schema, File
from typing import List, Optional
from datetime import date




class AuthUserRegistrationSchema(Schema):
    email:str
    username:str
    phone:str
    password:str
    passwordConfirm:str

class AuthUserRetrievalSchema(Schema):
    id:int=None
    email:str=None
    username:str=None
    # phone:str=None
    is_active:bool=None
    is_staff:bool=None
    is_superuser:bool=None
    
    
class UserLoginSchema(Schema):
    username_or_email: str
    password: str


# Schema for registration response
class TokenResponse(Schema):
    id: str
    username: str
    token: str
    
class RefreshTokenSchema(Schema):
    refresh_token: str


class ChangePasswordSchema(Schema):
    old_password: Optional[str]
    new_password: Optional[str]
    confirm_new_password: Optional[str]
