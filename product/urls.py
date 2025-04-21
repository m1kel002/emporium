from django.urls import path
from product.views import ListProductView, CreateProductView, ProductAPIView, ProductDetailAPIView

app_name = 'product'

urlpatterns = [
    path('', ProductAPIView.as_view(), name='product-list-create'),
    path('/<str:product_id>', ProductDetailAPIView.as_view(), name='product-detail'),
]