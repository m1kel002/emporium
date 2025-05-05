# get paginated reviews based on product
# create review
# delete review
from rest_framework import views, status
from rest_framework.response import Response
from core.pagination import CustomPagination
from review.serializers import ReviewSerializer, ReviewCreateSerializer
from core.models import Review
from rest_framework.permissions import IsAuthenticated, AllowAny


class ReviewAPIView(views.APIView):

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request):
        paginator = CustomPagination()
        reviews = Review.objects.all().order_by('-created_at')
        paginated_reviews = paginator.paginate_queryset(reviews, request)
        serializer = ReviewSerializer(paginated_reviews, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = ReviewCreateSerializer(data=request.data)
        if serializer.is_valid():
            review = serializer.save(created_by=self.request.user)
            response_serializer = ReviewSerializer(review)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)