from rest_framework import serializers
from core.models import Shop

class ShopSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shop
        fields = ['id', 'name', 'user', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_name(self, value):
        if Shop.objects.filter(name=value).exists():
            raise serializers.ValidationError('Shop name already exists')
        return value

class ShopShortInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shop
        fields = ['id', 'name']
