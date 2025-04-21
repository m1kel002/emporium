from rest_framework import serializers
from core.models import Cart, Product
from product.serializers import ProductShortInfoSerializer

class CartSerializer(serializers.ModelSerializer):
    product = ProductShortInfoSerializer(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'product', 'quantity', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

class CartCreateSerializer(CartSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta(CartSerializer.Meta):
        fields = CartSerializer.Meta.fields

