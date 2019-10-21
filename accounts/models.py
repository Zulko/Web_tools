from django.db import models


# Create your models here.


class News(models.Model):
    title = models.CharField(max_length=100)
    text = models.CharField(max_length=1000)
    author = models.CharField(max_length=30)
    created_at = models.DateField(auto_now_add=True)
