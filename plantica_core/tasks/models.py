from django.db import models
from django.conf import settings

class GardeningTask(models.Model):
    TASK_TYPE_CHOICES = [
        ('watering', 'Watering'),
        ('fertilizing', 'Fertilizing'),
        ('pruning', 'Pruning'),
        ('pesticide', 'Pesticide'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='gardening_tasks')
    user_plant = models.ForeignKey('plants.UserPlant', on_delete=models.CASCADE, related_name='tasks')
    task_type = models.CharField(max_length=30, choices=TASK_TYPE_CHOICES)
    scheduled_at = models.DateTimeField()
    is_completed = models.BooleanField(default=False)
    repeat_days = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.task_type} for {self.user_plant.nickname} - {self.scheduled_at}"
