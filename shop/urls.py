from django.urls import path
from shop.views import ListShopView, CreateShopView

app_name = 'shop'

urlpatterns = [
    path('', ListShopView.as_view(), name='shop-list'),
    path('/create', CreateShopView.as_view(), name='create')
]