from ninja import Schema
import uuid
from schemas.clients import *
from datetime import date


class ToDoRegistrationSchema(Schema):
    text:str=None
    # user_id:ClientRetrievalSchema=None
    
class ToDoRetrievalSchema(Schema):
    id:uuid.UUID=None
    text:str=None
    completed:bool=None
    user:ClientRetrievalSchema=None
    