from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Task(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    descr = models.CharField(max_length=12)
    due_date = models.DateField()
    done = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('task_detail', args=(self.id,))
