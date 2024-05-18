from decimal import Decimal, ROUND_HALF_UP

from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

from . import Currency, Country, AssetType, Account, Wallet

# class RetailBonds(models.Model):
    
#     name = models.CharField(max_length=100, blank=False, null=False)
#     code = models.CharField(max_length=100, blank=False, null=False)

#     description = models.CharField(blank=True, max_length=1000)
#     issuer = models.CharField(max_length=100, blank=False, null=False)
#     nominal_value = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])

#     price_currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
#     asset_type = models.ForeignKey(AssetType, on_delete=models.PROTECT)
#     current_value = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
#     initial_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])

#     premature_withdrawal_fee = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         abstract = True
    

# class TreasuryBonds(RetailBonds):

#     BOND_COUNTRIES = [country for country in Country.objects.all()]

#     def limit_to_bond_countries():
#         return {'name__in': [country.name for country in Country.objects.all()]}

#     issuer = models.ForeignKey(Country, on_delete=models.PROTECT, limit_choices_to=limit_to_bond_countries)

#     class Meta:
#         verbose_name = 'Government Bonds'
#         verbose_name_plural = 'Government Bonds'

#     def save(self, *args, **kwargs):

#         if self.issuer.name not in [country.name for country in Country.objects.all()]:
#             raise ValidationError('Issuer must be a country issuing government bonds.')

#         if self.issuer == Country.objects.get(name='Poland'):

#             self.nominal_value = Decimal('100.00')
#             self.price_currency = Currency.objects.get(code='PLN')
#             self.asset_type = AssetType.objects.get(name='Government Bonds')

#         self.asset_type = AssetType.objects.get(name='Government Bonds')

#         self.full_clean()
#         super().save(*args, **kwargs)


# class UserRetailBonds(models.Model):

#     user = models.ForeignKey('auth.User', related_name='assets', on_delete=models.CASCADE)
    
#     account = models.ForeignKey(Account, related_name='assets', on_delete=models.CASCADE)
#     wallet = models.ForeignKey(Wallet, related_name='assets', on_delete=models.CASCADE)
#     bond = models.ForeignKey(RetailBonds, related_name='assets', on_delete=models.CASCADE)

#     amount = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])

#     issue_date = models.DateField()
#     maturity_date = models.DateField()

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    

#     class Meta:
#         verbose_name = 'User Bonds'
#         verbose_name_plural = 'User Bonds'

#     def save(self, *args, **kwargs):

#         self.full_clean()
#         super().save(*args, **kwargs)

