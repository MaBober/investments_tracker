from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

from .abstract import BaseModel, validate_name_length


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=False, null=False)
    code = models.CharField(max_length=100, unique=True, blank=False, null=False)
    description = models.CharField(blank=True, max_length=1000)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Countries"
    
    def __str__(self):
        return self.name
        
    def save(self, *args, **kwargs):

        self.full_clean()
        super().save(*args, **kwargs)
    

class Currency(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=100, unique=True)
    symbol = models.CharField(max_length=100, blank=True)
    countries = models.ManyToManyField(Country, related_name='currencies')
    description = models.CharField(blank=True, max_length=1000)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Currencies"

    def __str__(self):
        return self.code


class CurrencyPrice(models.Model):
    currency = models.ForeignKey(Currency, related_name='prices', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=20, decimal_places=10, validators=[MinValueValidator(0)], default=0)
    date = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Currency Prices"
    
    def __str__(self):
        return f'{self.currency.code} - {self.price} - {self.date}'
    
    def save(self, *args, **kwargs):

        if self.id is not None:  # If the instance has already been saved to the database
            raise ValidationError('Updating a asset price is not allowed.')
        
        self.full_clean()
        super().save(*args, **kwargs)