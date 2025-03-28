from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        CUSTOMER = 'CUSTOMER', 'Customer'
        OUTLET = 'OUTLET', 'Outlet'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Card(models.Model):
    card_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cards'
    )
    is_active = models.BooleanField(default=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Card {self.card_number}"

class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        PAYMENT = 'PAYMENT', 'Payment'
        RECHARGE = 'RECHARGE', 'Recharge'
        SETTLEMENT = 'SETTLEMENT', 'Settlement'

    transaction_id = models.CharField(max_length=50, unique=True)
    transaction_type = models.CharField(
        max_length=10,
        choices=TransactionType.choices,
    )
    card = models.ForeignKey(
        Card,
        on_delete=models.PROTECT,
        related_name='transactions'
    )
    customer = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='customer_transactions'
    )
    outlet = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='outlet_transactions',
        null=True,
        blank=True
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('COMPLETED', 'Completed'),
            ('FAILED', 'Failed'),
        ],
        default='PENDING'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.transaction_id}"

class Settlement(models.Model):
    outlet = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='settlements'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('COMPLETED', 'Completed'),
            ('FAILED', 'Failed'),
        ],
        default='PENDING'
    )
    transactions = models.ManyToManyField(Transaction, related_name='settlements')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Settlement for {self.outlet.username} - {self.amount}"
