from django.db import models
from django.contrib.auth.models import User

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('TRANSFER', 'Transfer'),
    )
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)
