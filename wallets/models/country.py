from django.db import models
from django.core.exceptions import ValidationError

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
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    description = models.CharField(blank=True, max_length=1000)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Currencies"

    def __str__(self):
        return self.code
