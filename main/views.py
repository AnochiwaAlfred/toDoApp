from django.shortcuts import render, redirect
# from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Todo

# Create your views here.

def home(request):
    todo_items_not_completed = Todo.objects.filter(completed=False).order_by('created')
    todo_items_completed = Todo.objects.filter(completed=True).order_by('created')
    context = {
        "todo_items_not_completed":todo_items_not_completed,
        "todo_items_completed":todo_items_completed
          }
    return render(request, 'main/index.html', context)

def base(request):
    return render(request, 'base.html')

def add_todo(request):
    # print(request.POST.get('content'))
    # print(current_date)
    current_date = timezone.now()
    content = request.POST['content']
    Todo.objects.create(text =content, created=current_date)
    return redirect('/')

def delete_todo(request, todo_id):
    print(todo_id)
    Todo.objects.get(id=todo_id).delete()
    return redirect('/')

def completed_todo(request, todo_id):
    print(todo_id)
    item = Todo.objects.get(id=todo_id)
    item.completed = True
    item.save()
    return redirect('/')

def incomplete_todo(request, todo_id):
    print(todo_id)
    item = Todo.objects.get(id=todo_id)
    item.completed = False
    item.save()
    return redirect('/')
