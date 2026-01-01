"""
URL configuration for emporium project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings

from core.views import FileLocalUploadAPIView, GenerateUploadInfo

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('user.urls')),
    path('api/shop', include('shop.urls')),
    path('api/product', include('product.urls')),
    path('api/cart', include('cart.urls')),
    path('api/review', include('review.urls'))
]

if settings.DEBUG:
    urlpatterns.append(path('api/media/upload', GenerateUploadInfo.as_view()))
    urlpatterns.append(path('api/media/upload/local', FileLocalUploadAPIView.as_view()))
