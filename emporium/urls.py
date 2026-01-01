"""
URL configuration for emporium project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

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
    # serve image
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # generate upload url info
    urlpatterns.append(path('api/media/upload', GenerateUploadInfo.as_view()))
    # endpoint for upload file locally
    urlpatterns.append(path('api/media/upload/local', FileLocalUploadAPIView.as_view()))
