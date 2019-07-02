from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Task(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    descr = models.CharField(max_length=12)
    due_date = models.DateField()
    done = models.BooleanField(default=False)

    HIGH = 'high'
    LOW = 'low'
    PRIO = (
        (HIGH, HIGH),
        (LOW, LOW),
    )
    prio = models.CharField(max_length=4, choices=PRIO, default=LOW)

    def get_absolute_url(self):
        return reverse('task_detail', args=(self.id,))
