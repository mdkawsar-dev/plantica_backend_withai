from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import datetime

User = get_user_model()

class MasterPlant(models.Model):
    name_bn = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    scientific_name = models.CharField(max_length=150, blank=True, null=True)
    category = models.CharField(max_length=50)
    image = models.ImageField(upload_to='master_plants/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    suitable_sunlight = models.CharField(max_length=100, blank=True, null=True)
    suitable_season = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name_bn} ({self.name_en})"


class Plant(models.Model):
    LOCATION_CHOICES = (
        ('মাঝারি', 'মাঝারি'),
        ('ছাদ', 'ছাদ'),
        ('বারান্দা', 'বারান্দা'),
        ('ঘর', 'ঘর'),
        ('বাগান', 'বাগান'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='plants', null=True, blank=True)
    nickname = models.CharField(max_length=100, default='গাছ')
    species = models.CharField(max_length=100, default='চারাগাছ')
    planting_date = models.DateField(default=datetime.date.today)
    location = models.CharField(max_length=50, choices=LOCATION_CHOICES, default='বারান্দা')
    image = models.ImageField(upload_to='plants/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.nickname} ({self.species})"

    @property
    def age_display(self):
        today = datetime.date.today()
        delta = today - self.planting_date
        
        days = delta.days
        if days < 0:
            return "সদ্য রোপণকৃত"
            
        months = days // 30
        remaining_days = days % 30
        years = months // 12
        remaining_months = months % 12

        if years > 0:
            return f"{years} বছর {remaining_months} মাস"
        elif remaining_months > 0:
            return f"{remaining_months} মাস {remaining_days} দিন"
        else:
            return f"{remaining_days} দিন"


class UserPlant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_plants')
    plant_info = models.ForeignKey(MasterPlant, on_delete=models.CASCADE, related_name='user_instances', null=True, blank=True)
    nickname = models.CharField(max_length=100)
    planted_date = models.DateField(default=datetime.date.today)
    location = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='user_plants/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, default='healthy')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.nickname} ({self.user.username})"


class PlantTask(models.Model):
    TASK_TYPES = (
        ('পানি দেওয়া', 'পানি দেওয়া'),
        ('সার দেওয়া', 'সার দেওয়া'),
        ('ছাঁটাই', 'ছাঁটাই'),
        ('কীটনাশক', 'কীটনাশক'),
    )

    REPEAT_CHOICES = (
        ('একবার', 'একবার'),
        ('দৈনিক', 'দৈনিক'),
        ('সপ্তাহে একবার', 'সপ্তাহে একবার'),
        ('মাসে একবার', 'মাসে একবার'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='tasks')
    task_type = models.CharField(max_length=50, choices=TASK_TYPES)
    due_date = models.DateField(default=datetime.date.today)
    due_time = models.TimeField(default=datetime.time(9, 0))
    repeat_frequency = models.CharField(max_length=50, choices=REPEAT_CHOICES, default='একবার')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.task_type} - {self.plant.nickname}"


class DistrictPlantRecommendation(models.Model):
    district = models.CharField(max_length=100)
    plant_name_bn = models.CharField(max_length=100)
    plant_name_en = models.CharField(max_length=100)
    sunlight = models.CharField(max_length=50)
    space = models.CharField(max_length=50)
    season = models.CharField(max_length=50)
    soil_type = models.CharField(max_length=50)
    watering_info = models.TextField()
    fertilizer_info = models.TextField()
    harvest_time = models.TextField()
    growth_time = models.CharField(max_length=50)
    difficulty = models.CharField(max_length=50)
    care_tips = models.TextField()
    extra_description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='plant_recommendations/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.plant_name_bn} - {self.district}"
