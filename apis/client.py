from ninja import FormEx, Router, UploadedFile, FileEx
from django.db.models import Q
from typing import List, Union
from schemas.clients import *
from users.models import *


router = Router(tags=["Clients Router"])

@router.get('clients/list', response=List[ClientRetrievalSchema])
def list_clients(request):
    clients = Client.objects.all()
    return clients

@router.get('client/{client_id}/get', response=Union[str, ClientRetrievalSchema])
def get_client_by_id(request, client_id):
    clientInstance = Client.objects.filter(id=client_id)
    if clientInstance.exists():
        return clientInstance[0]
    return f"Client with ID {client_id} does not exist"
    
    
@router.post('client/add', response=Union[str, ClientRetrievalSchema])
def add_client(request, image:UploadedFile, password:str=None, data:ClientRegistrationSchema=FormEx(...)):
    client = Client.objects.create(**data.dict())
    client.set_password(password)
    client.image = image
    client.save()
    return client
    

@router.post('client/{client_id}/update_image', response=Union[str, ClientRetrievalSchema])
def update_image(request, client_id, image:UploadedFile=FileEx(...)):
    clientInstance = Client.objects.filter(id=client_id)
    if clientInstance.exists():
        client = clientInstance[0]
        client.image=image
        client.save()
        return client
    return f"Client with ID {client_id} does not exist"
    
@router.delete('/client/{client_id}/delete')
def delete_client(request, client_id):
    clientInstance = Client.objects.filter(id=client_id)
    if clientInstance.exists():
        client = clientInstance[0]
        client.delete()
        return f"Client {client.username} deleted successfully"
    return f"Client with ID {client_id} does not exist"