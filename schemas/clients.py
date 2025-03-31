from ninja import Schema, File
from typing import List
from datetime import date




class ClientRegistrationSchema(Schema):
    email:str=None
    username:str=None
    phone:str=None
    password:str=None
    passwordConfirm:str=None

class ClientRetrievalSchema(Schema):
    id:int=None
    email:str=None
    username:str=None
    phone:str=None
    # image:str=None