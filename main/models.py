from django.db import models

# Create your models here.

class Todo(models.Model):
    added_date = models.DateTimeField()
    text = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.text}'
        
    class Meta:
        verbose_name = f'ToDo Item'
        verbose_name_plural = 'Items To Do'