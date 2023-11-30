from django.db import models
from users.models import CustomUser
from plugins.generate_filename import generate_filename


class Client(CustomUser):
    image = models.ImageField(null=True, blank=True, upload_to=generate_filename)

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return self.username
