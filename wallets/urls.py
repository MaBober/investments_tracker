from django.urls import path

from rest_framework.urlpatterns import format_suffix_patterns

from . import views

wallets_list = views.WalletViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

wallets_detail = views.WalletViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})

accounts_list = views.AccountViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

accounts_detail = views.AccountViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})

deposit_list = views.DepositViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

deposit_detail = views.DepositViewSet.as_view({
    'get': 'retrieve',
    #'put': 'update',
    'delete': 'destroy'
})

market_transaction_list = views.MarketAssetTransactionViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

market_transaction_detail = views.MarketAssetTransactionViewSet.as_view({
    'get': 'retrieve',
    #'put': 'update',
    #'delete': 'destroy'
})

treasury_bond_transaction_list = views.TreasuryBondsTransactionViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

treasury_bond_transaction_detail = views.TreasuryBondsTransactionViewSet.as_view({
    'get': 'retrieve',
    #'put': 'update',
    #'delete': 'destroy'
})

withdrawal_list = views.WithdrawalViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

withdrawal_detail = views.WithdrawalViewSet.as_view({
    'get': 'retrieve',
    #'put': 'update',
    'delete': 'destroy'
})


urlpatterns = [
    path('wallets/', wallets_list, name='wallets-list'),
    path('wallets/<int:pk>/', wallets_detail, name='wallets-detail'),
    path('accounts/', accounts_list, name='accounts-list'),
    path('accounts/<int:pk>/', accounts_detail, name='accounts-detail'),
    path('deposits/', deposit_list, name='deposit-list'),
    path('deposits/<int:pk>/', deposit_detail, name='deposit-detail'),
    path('market_transactions/', market_transaction_list, name='market_transaction-list'),
    path('market_transactions/<int:pk>/', market_transaction_detail, name='market_transaction-detail'),
    path('treasury_bond_transactions/', treasury_bond_transaction_list, name='treasury_bond_transaction-list'),
    path('treasury_bond_transactions/<int:pk>/', treasury_bond_transaction_detail, name='treasury_bond_transaction-detail'),
    path('withdrawals/', withdrawal_list, name='withdrawal-list'),
    path('withdrawals/<int:pk>/', withdrawal_detail, name='withdrawal-detail'),
    path('users/', views.UserList.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetail.as_view()),
    path('accounts/<int:account_id>/transactions/', views.ObjectMarketTransactionsList.as_view(), name='account-transactions'),
    path('accounts/<int:account_id>/treasury_bond_transactions/', views.ObjectTreasuryBondsTransactionsList.as_view(), name='account-treasury-bond-transactions'),
    path('accounts/<int:account_id>/market_assets/', views.ObjectUserAssetsList.as_view(), name='account-assets'),
    path('accounts/<int:account_id>/treasury_bonds/', views.ObjectUserTreasuryBondsList.as_view(), name='account-treasury-bonds'),
    path('wallets/<int:wallet_id>/transactions/', views.ObjectMarketTransactionsList.as_view(), name='wallet-transactions'),
    path('wallets/<int:wallet_id>/treasury_bond_transactions/', views.ObjectTreasuryBondsTransactionsList.as_view(), name='wallet-treasury-bond-transactions'),
    path('wallets/<int:wallet_id>/market_assets/', views.ObjectUserAssetsList.as_view(), name='wallet-assets'),
    path('wallets/<int:wallet_id>/treasury_bonds/', views.ObjectUserTreasuryBondsList.as_view(), name='wallet-treasury-bonds'),
    path('users/<int:user_id>/transactions/', views.ObjectMarketTransactionsList.as_view(), name='user-transactions'),
    path('users/<int:user_id>/treasury_bond_transactions/', views.ObjectTreasuryBondsTransactionsList.as_view(), name='user-treasury-bond-transactions'),
    path('users/<int:user_id>/market_assets/', views.ObjectUserAssetsList.as_view(), name='user-assets'),
    path('users/<int:user_id>/treasury_bonds/', views.ObjectUserTreasuryBondsList.as_view(), name='user-treasury-bonds'),
    path('account/test/', views.AccountTest, name='account-test'),
    
]

urlpatterns = format_suffix_patterns(urlpatterns)
