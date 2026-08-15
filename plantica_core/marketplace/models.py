from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class MarketplaceListing(models.Model):
    CATEGORY_CHOICES = (
        ('বীজ', 'বীজ'),
        ('চারাগাছ', 'চারাগাছ'),
        ('টব', 'টব'),
        ('সার', 'সার'),
        ('টুলস', 'পার্টনার টুলস'),
    )

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=150)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.CharField(max_length=50)
    description = models.TextField()
    contact_number = models.CharField(max_length=15)
    location = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='marketplace_items/', blank=True, null=True)
    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
