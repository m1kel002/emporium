from django.urls import path
from review.views import ReviewAPIView

app_name = 'review'

urlpatterns = [
    path('', ReviewAPIView.as_view(), name='review-list-create')
]