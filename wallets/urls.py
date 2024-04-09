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

urlpatterns = [
    path('wallets/', wallets_list, name='wallets-list'),
    path('wallets/<int:pk>/', wallets_detail, name='wallets-detail'),
    path('accounts/', accounts_list, name='accounts-list'),
    path('accounts/<int:pk>/', accounts_detail, name='accounts-detail'),
    path('users/', views.UserList.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetail.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)
