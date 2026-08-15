from django.db import models
from django.conf import settings

class DiseaseInfo(models.Model):
    RISK_LEVEL_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    plant = models.ForeignKey('plants.Plant', on_delete=models.CASCADE, related_name='diseases')
    class_index = models.IntegerField(unique=True)
    disease_name_bn = models.CharField(max_length=255)
    disease_name_en = models.CharField(max_length=255)
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES)
    treatment_bn = models.TextField()
    prevention_bn = models.TextField()

    def __str__(self):
        return f"[{self.class_index}] {self.disease_name_bn} ({self.disease_name_en})"


class DiseaseDiagnosisLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='diagnosis_logs')
    user_plant = models.ForeignKey('plants.UserPlant', on_delete=models.SET_NULL, null=True, blank=True, related_name='diagnosis_logs')
    uploaded_image = models.ImageField(upload_to='diagnosis_scans/')
    predicted_disease = models.ForeignKey(DiseaseInfo, on_delete=models.SET_NULL, null=True, blank=True, related_name='diagnosis_logs')
    confidence_score = models.FloatField(null=True, blank=True)
    is_confirmed_by_user = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Scan by {self.user.username} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"
