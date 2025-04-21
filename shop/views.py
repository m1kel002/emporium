from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from core.models import Shop
from shop.serializers import ShopSerializer
from rest_framework.authentication import TokenAuthentication

class ListShopView(generics.ListAPIView):
    serializer_class = ShopSerializer

    def get_queryset(self):
        queryset = Shop.objects.all()
        shop_name = self.request.query_params.get('name')
        if shop_name:
            queryset = queryset.filter(name__icontains=shop_name)
        return queryset

class CreateShopView(generics.CreateAPIView):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user, created_by=self.request.user)
