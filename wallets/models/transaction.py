# from django.db import models
# from django.core.exceptions import ValidationError

# from . import  Account

# class Transaction(models.Model):
#     """
#     Transaction model

#     Attributes:
#     -----
#     asset: models.ForeignKey
#         The asset bought in the transaction
#     account: models.ForeignKey
#         The account with which the transaction is associated
#     type: models.CharField
#         The type of the bought asset
#     quantity: models.DecimalField
#         The quantity of the bought asset
#     price: models.DecimalField
#         The price of the bought asset
#     currency: models.CharField
#         The currency of the bought asset
#     commission: models.DecimalField
#         The commission of the transaction
#     commission_currency: models.CharField
#         The currency of the commission
#     description: models.TextField
#         The description of the transaction
#     bought_at: models.DateTimeField
#         The date and time the asset was bought
#     created_at: models.DateTimeField
#         The date and time the transaction was created
#     updated_at: models.DateTimeField
#         The date and time the transaction was last updated
    
#     Relationships:
#     -----
#     asset: Asset
#         The asset bought in the transaction
#     account: Account
#         The account with which the transaction is associated
    
#     Methods:
#     -----
#     __str__:
#         Returns the type of the bought asset
    
#     """
#     # asset = models.ForeignKey(Asset, related_name='transactions', on_delete=models.CASCADE)
#     account = models.ForeignKey(Account, related_name='transactions', on_delete=models.CASCADE)
#     type = models.CharField(max_length=100)
#     quantity = models.DecimalField(max_digits=12, decimal_places=2)
#     price = models.DecimalField(max_digits=12, decimal_places=2)
#     currency = models.CharField(max_length=100, default='PLN')
#     commission = models.DecimalField(max_digits=12, decimal_places=2)
#     commission_currency = models.CharField(max_length=100, default='PLN')
#     description = models.TextField(blank=True)
#     bought_at = models.DateTimeField()
    
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.type
