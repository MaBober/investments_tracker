from django.db import models
from django.core.exceptions import ValidationError

def validate_name_length(value):
    if len(value) < 3:
        raise ValidationError('Name must be at least 3 characters long')

class BaseModel(models.Model):

    class Meta:
        abstract = True

    def clean(self):
        if self.id:
            if self.owner and self.co_owners.filter(id=self.owner.id).exists():
                raise ValidationError('The owner and co-owner must be different users')
        
    def save(self, *args, **kwargs):

        self.full_clean()
        super().save(*args, **kwargs)