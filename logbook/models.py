from django.db import models
from db.models import Machine

# Create your models here.


class LogBook(models.Model):
    # name = models.CharField(max_length=30, default='')
    user = models.CharField(max_length=30,)
    supervisor = models.CharField(max_length=100)
    time_used = models.CharField(max_length=30, blank=True)
    comments = models.CharField(max_length=100, blank=True)
    created_at = models.DateField(auto_now_add=True)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)

    # Meta Class
    # class Meta:
    #     ordering = ('machine','user')
    #
    # def __str__(self):
    #     return self.machine