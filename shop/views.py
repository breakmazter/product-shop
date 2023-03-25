from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, Http404
from django.template import loader

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import ProductSerializer, CategorySerializer
from .models import Product, Category


def index(request: WSGIRequest) -> HttpResponse:
    template = loader.get_template('index.html')
    return HttpResponse(template.render({}, request))


class ProductDetail(APIView):
    @staticmethod
    def get_product(pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404

    @staticmethod
    def get_category(data):
        try:
            category = Category.objects.get(id=data.get('id'))
        except Category.DoesNotExist:
            category_serializer = CategorySerializer(data=data)

            if category_serializer.is_valid():
                category = category_serializer.save()
            else:
                return Response(category_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return category

    def post(self, request):
        category_data = request.data.get('category')

        category = self.get_category(data=category_data)

        request.data['category'] = category.id

        product_serializer = ProductSerializer(data=request.data)

        if product_serializer.is_valid():
            product_serializer.save(category=category)
            return Response(product_serializer.data, status=status.HTTP_201_CREATED)

        return Response(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        product = self.get_product(pk)

        category_data = request.data.get('category')

        category = self.get_category(data=category_data)

        request.data['category'] = category.id

        product_serializer = ProductSerializer(product, data=request.data, partial=True)

        if product_serializer.is_valid():
            product_serializer.save(category=category)
            return Response(product_serializer.data, status=status.HTTP_201_CREATED)

        return Response(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
