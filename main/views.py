from django.shortcuts import render, redirect
# from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Todo

# Create your views here.

def home(request):
    todo_items = Todo.objects.all().order_by('added_date')
    context = {"todo_items":todo_items}
    return render(request, 'main/index.html', context)

def base(request):
    return render(request, 'base.html')

def add_todo(request):
    # print(request.POST.get('content'))
    # print(current_date)
    current_date = timezone.now()
    content = request.POST['content']
    Todo.objects.create(text =content, added_date=current_date)
    return redirect('/')

def delete_todo(request, todo_id):
    print(todo_id)
    Todo.objects.get(id=todo_id).delete()
    return redirect('/')

def completed_todo(request, todo_id):
    print(todo_id)
    item = Todo.objects.get(id=todo_id)
    if item.completed == True:
        item.completed = False
        # item.input_tag(attrs={'class':'disabled'})
        
    else:
        item.completed = True
    item.save()
    return redirect('/')