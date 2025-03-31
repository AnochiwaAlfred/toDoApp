from ninja import FormEx, Router, UploadedFile, FileEx
from ninja.errors import HttpError
from django.db.models import Q  
from typing import List, Union
from schemas.clients import *
from users.models import *
from .auth2 import JWTAuth, create_jwt_tokens


router = Router(tags=["Clients Router"])

@router.get('clients/list', auth=None, response=Union[List[ClientRetrievalSchema], str])
def list_clients(request):
    return Client.objects.all()

@router.get('client/{client_id}/get', response=Union[str, ClientRetrievalSchema], auth=JWTAuth())
def get_client_by_id(request, client_id):
    client = Client.objects.filter(id=client_id).first()
    if not client:
        error = f"Client with ID {client_id} does not exist"
        return str(HttpError(401, error))
    return client
    
    
@router.post('client/add', response=Union[ClientRetrievalSchema, str])
def add_client(request, data:ClientRegistrationSchema=FormEx(...)):
     # Validate uniqueness
    if Client.objects.filter(username=data.username).exists():
        return str(HttpError(400, "Username already exists"))
    if Client.objects.filter(email=data.email).exists():
        return str(HttpError(400, "Email already in use"))
    if data.password != data.passwordConfirm:
        return str(HttpError(400, "Passwords do not match"))
    # Create client
    client = Client.objects.create(
        username=data.username,
        email=data.email,
        phone=data.phone
    )
    client.set_password(data.password)
    client.save()
    return client
    

@router.post('client/{client_id}/update_image', response=Union[str, ClientRetrievalSchema], auth=JWTAuth())
def update_image(request, client_id, image:UploadedFile=FileEx(...)):
    client = Client.objects.filter(id=client_id).first()
    if not client:
        error = f"Client with ID {client_id} does not exist"
        return str(HttpError(401, error))
  
    # client.image=image
    client.image.save(image.name, image)
    client.save()
    return client
    
@router.delete('/client/{client_id}/delete', auth=JWTAuth())
def delete_client(request, client_id):
    client = Client.objects.filter(id=client_id).first()
    if not client:
        return str(HttpError(404, f"Client with ID {client_id} does not exist"))

    client.delete()
    return {"message": f"Client {client.username} deleted successfully"}
