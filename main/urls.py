from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('base', views.base, name='base'),
    path('add_todo', views.add_todo, name='add_todo'),
    path('delete_todo/<int:todo_id>/', views.delete_todo, name='delete_todo'),
    path('completed_todo/<int:todo_id>/', views.completed_todo, name='completed_todo'),
    path('incomplete_todo/<int:todo_id>/', views.incomplete_todo, name='incomplete_todo'),
]
