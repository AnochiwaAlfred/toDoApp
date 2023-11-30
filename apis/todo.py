from ninja import FormEx, Router
from django.db.models import Q
from typing import List, Union
from schemas.todo import *
from schemas.clients import *
from main.models import *
from users.models import *



router = Router(tags=["Todo Endpoints"])

@router.get('/client/{user_id}/list_todos', response=List[ToDoRetrievalSchema])
def list_client_todos(request, user_id):
    todos = Todo.objects.filter(user_id=user_id)
    return todos

@router.get('/client/{user_id}/list_client_completed_todos', response=List[ToDoRetrievalSchema])
def list_client_completed_todos(request, user_id):
    todos = Todo.objects.filter(user_id=user_id, completed=True)
    return todos

@router.get('/client/{user_id}/list_incomplete_todos', response=List[ToDoRetrievalSchema])
def list_client_incomplete_todos(request, user_id):
    todos = Todo.objects.filter(user_id=user_id, completed=False)
    return todos

@router.post('/client/{user_id}/todo/create/{text}', response=Union[str, ToDoRetrievalSchema])
def create_todo(request, user_id, text:str):
    if text != "":
        todo = Todo.objects.create(user_id=user_id, text=text)
        return todo
    return f"Error: Empty text field"
        

@router.put('/todo/{todo_id}/update/{text}', response=Union[str, ToDoRetrievalSchema])
def update_todo(request, todo_id, text:str):
    todoInst = Todo.objects.filter(id=todo_id)
    if todoInst.exists():
        todo = todoInst[0]
        # if text != "":
        print(text)
        print(todo.text)
        todo.text=text
        todo.save()
        return todo
        # return f"Error: Empty text field"
    return f"Todo with ID {todo_id} does not exist"

@router.put('/todo/{todo_id}/mark_completed', response=Union[str, ToDoRetrievalSchema])
def mark_todo_completed(request, todo_id):
    todoInst = Todo.objects.filter(id=todo_id)
    if todoInst.exists():
        todo = todoInst[0]
        todo.completed = True
        todo.save()
        return todo
    return f"Todo with ID {todo_id} does not exist"
    
@router.put('/todo/{todo_id}/mark_incomplete', response=Union[str, ToDoRetrievalSchema])
def mark_todo_incomplete(request, todo_id):
    todoInst = Todo.objects.filter(id=todo_id)
    if todoInst.exists():
        todo = todoInst[0]
        todo.completed = False
        todo.save()
        return todo
    return f"Todo with ID {todo_id} does not exist"


    
@router.delete('/todo/{todo_id}/delete', response=Union[str, ToDoRetrievalSchema])
def delete_todo(request, todo_id):
    todoInst = Todo.objects.filter(id=todo_id)
    if todoInst.exists():
        todo = todoInst[0]
        todo.delete() 
        return f"Todo deleted successfullt"
    return f"Todo with ID {todo_id} does not exist"