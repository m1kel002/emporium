from django.urls import path
from cart.views import CartAPIView, CartDetailAPIView

app_name = 'cart'

urlpatterns = [
    path('', CartAPIView.as_view(), name='cart'),
    path('/<str:cart_id>', CartDetailAPIView.as_view(), name='cart-detail')
]