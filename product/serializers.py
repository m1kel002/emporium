from rest_framework import serializers
from core.models import Product, Shop
from shop.serializers import ShopShortInfoSerializer

class ProductSerializer(serializers.ModelSerializer):
    shop = ShopShortInfoSerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'quantity', 'shop', 'image', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_price(self, value):
        if value <= 0:
            serializers.ValidationError('Product price must be greater than zero', code='invalid')
        return value

    def validate_quantity(self, value):
        if value <=0:
            serializers.ValidationError('Quantity must be greater than zero')
        return value

    def validate_name(self, value):
        if len(value.replace(' ', '')) <= 0:
            serializers.ValidationError('Product name is invalid')
        return value

class ProductCreateSerializer(ProductSerializer):
    shop = serializers.PrimaryKeyRelatedField(queryset=Shop.objects.all())

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields


class ProductShortInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'image']