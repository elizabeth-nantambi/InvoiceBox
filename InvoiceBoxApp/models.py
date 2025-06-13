from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
# Create your models here.
class Invoice(models.Model):
    CURRENCY_CHOICES = [
        ('UGX', 'Ugandan Shilling'),
        ('USD', 'US Dollar'),
        ('LYD', 'Libyan Dinar'),
        
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('defaulted', 'Defaulted'),
    ]

    provider = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='provided_invoices', on_delete=models.CASCADE)
    purchaser = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_invoices', on_delete=models.CASCADE)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    date_created = models.DateTimeField(auto_now_add=True)
    date_due = models.DateTimeField()
    date_paid = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Invoice {self.id} from {self.provider.username} to {self.purchaser.username} - {self.amount} {self.currency}"

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('provider', 'Provider'),
        ('purchaser', 'Purchaser'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    date_paid = models.DateTimeField(auto_now_add=True)
    
