from django.db import models
from django.conf import settings

class GardeningExpense(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='expenses')
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    receipt_image = models.ImageField(upload_to='expense_receipts/', null=True, blank=True)

    def __str__(self):
        return f"{self.title} - ৳{self.amount} ({self.user.username})"
