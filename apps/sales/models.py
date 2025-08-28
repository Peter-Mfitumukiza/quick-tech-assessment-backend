from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)
    category = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        db_table = 'products'

    def __str__(self):
        return self.name


class Sale(models.Model):
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        related_name='sales'
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    sold_at = models.DateField()
    total = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sold_at', '-created_at']
        db_table = 'sales'
        indexes = [
            models.Index(fields=['sold_at']),
            models.Index(fields=['product', 'sold_at']),
        ]

    def save(self, *args, **kwargs):
        # Auto-calculate total if not provided
        if not self.total:
            self.total = self.quantity * self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} units on {self.sold_at}"


class DailyAggregate(models.Model):
    date = models.DateField(unique=True)
    total_revenue = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        default=Decimal('0.00')
    )
    total_orders = models.PositiveIntegerField(default=0)
    total_units = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        db_table = 'daily_aggregates'
        indexes = [
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"Aggregate for {self.date}: ${self.total_revenue}"