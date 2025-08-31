from rest_framework import generics, views
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from product.serializers import (ProductDetailSerializer, ProductSerializer,
                                 ProductCreateSerializer)
from core.models import Product
from core.pagination import CustomPagination


class ListProductView(generics.ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = Product.objects.all()
        shop = self.request.query_params.get('shop')
        if shop:
            queryset = queryset.filter(shop__id__exact=shop)
        return queryset


class CreateProductView(generics.CreateAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        return serializer.save(created_by=self.request.user)

class ProductAPIView(views.APIView):

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request):
        paginator = CustomPagination()
        products = Product.objects.all().filter(quantity__gt=0)
        shop = request.query_params.get('shop')
        search_param = request.query_params.get('search')
        category_param = request.query_params.get('category')
        if shop:
            products = products.filter(shop__id__exact=shop)
        if search_param:
            products = products.filter(name__icontains=search_param)
        if category_param:
            products = products.filter(category__iexact=category_param)
        paginated_products = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(paginated_products, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = ProductCreateSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save(created_by=self.request.user)
            response_serializer = ProductSerializer(product)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailAPIView(views.APIView):

    def get_permissions(self):
        method = self.request.method
        if (method == 'POST' or
            method == 'PATCH' or
            method == 'DELETE'):
            return [IsAuthenticated()]
        else:
            return [AllowAny()]

    def get(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        serializer = ProductDetailSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        serializer = ProductCreateSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            product = serializer.save()
            response_serializer = ProductSerializer(product)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        product.delete()
        return Response({'message': 'Product successfully deleted'}, status=status.HTTP_200_OK)