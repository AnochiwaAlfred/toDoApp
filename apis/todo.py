import uuid
from typing import List, Union

from django.db.models import Q
from django.http import JsonResponse

from ninja import FormEx, Router
from ninja.errors import HttpError

from .auth2 import JWTAuth
from schemas.todo import *
from schemas.clients import *
from main.models import *
from users.models import *


router = Router(tags=["Todo Endpoints"])
auth = JWTAuth()


@router.get('/client/{user_id}/list_todos', auth=auth, response=Union[List[ToDoRetrievalSchema], dict])
def list_client_todos(request, user_id):
    todos = Todo.objects.filter(user_id=user_id)
    if not todos.exists():
        return JsonResponse({"error": "No todos found for this client"}, status=404)
    return todos

@router.get('/client/{user_id}/list_client_completed_todos', auth=auth, response=Union[List[ToDoRetrievalSchema], dict])
def list_client_completed_todos(request, user_id):
    todos = Todo.objects.filter(user_id=user_id, completed=True)
    if not todos.exists():
        return JsonResponse({"error": "No completed todos found for this client"}, status=404)
    return todos

@router.get('/client/{user_id}/list_incomplete_todos', auth=auth, response=Union[List[ToDoRetrievalSchema], dict])
def list_client_incomplete_todos(request, user_id):
    todos = Todo.objects.filter(user_id=user_id, completed=False)
    if not todos.exists():
        return JsonResponse({"error": "No incomplete todos found for this client"}, status=404)
    return todos

@router.post('/client/{user_id}/todo/create', auth=auth, response=Union[ToDoRetrievalSchema, dict])
def create_todo(request, user_id: int, data: ToDoRegistrationSchema = FormEx(...)):
    if not data.text:
        return JsonResponse({"error": "Text field must not be empty"}, status=400)
    todo = Todo.objects.create(user_id=user_id, text=data.text)
    return todo



@router.put('/todo/{todo_id}/update', auth=auth, response=Union[ToDoRetrievalSchema, dict])
def update_todo(request, todo_id: uuid.UUID, data: ToDoUpdateSchema): 
    todo = Todo.objects.filter(id=todo_id).first()
    if not todo:
        return JsonResponse({"error": f"Todo with ID {todo_id} does not exist"}, status=404)
    
    if not data.text:
        return JsonResponse({"error": "Text field must not be empty"}, status=400)
    
    todo.text = data.text
    todo.save()
    return todo


@router.put('/todo/{todo_id}/mark_completed', auth=auth, response=Union[ToDoRetrievalSchema, dict])
def mark_todo_completed(request, todo_id):
    todo = Todo.objects.filter(id=todo_id).first()
    if not todo:
        return JsonResponse({"error": f"Todo with ID {todo_id} does not exist"}, status=404)
    
    todo.completed = True
    todo.save()
    return todo

@router.put('/todo/{todo_id}/mark_incomplete', auth=auth, response=Union[ToDoRetrievalSchema, dict])
def mark_todo_incomplete(request, todo_id):
    todo = Todo.objects.filter(id=todo_id).first()
    if not todo:
        return JsonResponse({"error": f"Todo with ID {todo_id} does not exist"}, status=404)
    
    todo.completed = False
    todo.save()
    return todo

@router.delete('/todo/{todo_id}/delete', auth=auth, response=Union[dict, dict])
def delete_todo(request, todo_id):
    todo = Todo.objects.filter(id=todo_id).first()
    if not todo:
        return JsonResponse({"error": f"Todo with ID {todo_id} does not exist"}, status=404)
    
    todo.delete()
    return JsonResponse({"message": "Todo deleted successfully"}, status=200)
