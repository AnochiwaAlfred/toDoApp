from django.db import models
import uuid
from django.utils import timezone

# Create your models here.

class Todo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    user = models.ForeignKey('users.Client', null=True, blank=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_created=True, default=timezone.now, editable=False)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.text}'
        
    class Meta:
        verbose_name = f'ToDo Item'
        verbose_name_plural = 'Items To Do'
        
