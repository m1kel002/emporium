from rest_framework import serializers
from core.models import Product, Review
from product.serializers import ProductShortInfoSerializer
from user.serializers import UserShortInfoSerializer

class ReviewSerializer(serializers.ModelSerializer):
    product = ProductShortInfoSerializer(read_only=True)
    user = UserShortInfoSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'message', 'rating', 'product', 'user', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_rating(self, value):
        if 0 < value <= 5:
            return value
        raise serializers.ValidationError('Rating must be between 1 and 5 inclusive')

class ReviewCreateSerializer(ReviewSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta(ReviewSerializer.Meta):
        fields = ReviewSerializer.Meta.fields
