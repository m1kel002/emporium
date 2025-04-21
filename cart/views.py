from rest_framework import views
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from cart.serializers import CartCreateSerializer, CartSerializer
from core.pagination import CustomPagination
from core.models import Cart

class CartAPIView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        paginator = CustomPagination()
        cart_items = Cart.objects.all()
        user = self.request.user
        items = cart_items.filter(user=user)
        paginated_items = paginator.paginate_queryset(items, request)
        serializer = CartSerializer(paginated_items, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = CartCreateSerializer(data=request.data)
        if serializer.is_valid():
            cart = serializer.save(user=self.request.user, created_by=self.request.user)
            response_serializer = CartSerializer(cart)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CartDetailAPIView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, cart_id):
        cart = get_object_or_404(Cart, pk=cart_id)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, cart_id):
        cart = get_object_or_404(Cart, pk=cart_id)
        serializer = CartCreateSerializer(cart, data=request.data, partial=True)
        if serializer.is_valid():
            updated_cart = serializer.save()
            response_serializer = CartSerializer(updated_cart)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, cart_id):
        cart = get_object_or_404(Cart, pk=cart_id)
        cart.delete()
        return Response({'message': 'Cart successfully deleted'}, status=status.HTTP_200_OK)