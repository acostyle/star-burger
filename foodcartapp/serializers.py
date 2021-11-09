from rest_framework.serializers import ModelSerializer

from .models import Order, OrderedProduct


class OrderedProductSerializer(ModelSerializer):
    class Meta:
        model = OrderedProduct
        fields = ['id', 'product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderedProductSerializer(many=True, allow_empty=False, write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'products', 'firstname', 'lastname', 'phonenumber', 'address']