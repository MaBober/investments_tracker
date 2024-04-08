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

urlpatterns = [
    path('wallets/', wallets_list, name='wallets-list'),
    path('wallets/<int:pk>/', wallets_detail, name='wallets-detail'),
    path('users/', views.UserList.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetail.as_view()),
    path('change-password', views.change_password, name='change-password')
]

urlpatterns = format_suffix_patterns(urlpatterns)
