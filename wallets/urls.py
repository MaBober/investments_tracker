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

transaction_list = views.MarketAssetTransactionViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

transaction_detail = views.MarketAssetTransactionViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
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
    path('transactions/', transaction_list, name='transaction-list'),
    path('transactions/<int:pk>/', transaction_detail, name='transaction-detail'),
    path('withdrawals/', withdrawal_list, name='withdrawal-list'),
    path('withdrawals/<int:pk>/', withdrawal_detail, name='withdrawal-detail'),
    path('users/', views.UserList.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetail.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)
