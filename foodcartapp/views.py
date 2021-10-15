from django.db import transaction
from django.http import JsonResponse
from django.templatetags.static import static

from geopy import distance
from foodcartapp.location import fetch_coordinates
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from star_burger import settings
from .models import Order
from .models import OrderedProduct
from .models import Product
from .models import RestaurantMenuItem


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['GET'])
def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            },
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return Response(dumped_products)


class OrderedProductSerializer(ModelSerializer):
    class Meta:
        model = OrderedProduct
        fields = ['id', 'product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderedProductSerializer(many=True, allow_empty=False, write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'products', 'firstname', 'lastname', 'phonenumber', 'address']


@transaction.atomic
@api_view(['POST'])
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    order = Order.objects.create(
        firstname=serializer.validated_data['firstname'],
        lastname=serializer.validated_data['lastname'],
        phonenumber=serializer.validated_data['phonenumber'],
        address=serializer.validated_data['address']
    )

    product_fields = serializer.validated_data['products']
    OrderedProduct.objects.bulk_create([OrderedProduct(order=order, **fields) for fields in product_fields])
    order_serializer = OrderSerializer(order)

    return Response(order_serializer.data)

def get_available_restaurants_with_products(order):
    products_in_restaurants = RestaurantMenuItem.objects.prefetch_related('restaurant', 'product').filter(availability=True)
    order_products = order.ordered_products.all()

    restaurants_with_needed_products = []
    for order_product in order_products:
        for product_in_restaurants in products_in_restaurants:
            if product_in_restaurants.product == order_product.product:
                restaurants_with_needed_products.append(product_in_restaurants.restaurant)
    
    return calculate_distances_to_order(
        restaurants_with_needed_products,
        settings.YA_API_KEY,
        order.address
    )

def calculate_distances_to_order(restaurants, ya_api_key, order_address):
    order_lon, order_lat = fetch_coordinates(ya_api_key, order_address)
    restaurants_with_order_distance = []
    for restaurant in restaurants:
        restaurant_lon, restaurant_lat = fetch_coordinates(ya_api_key, restaurant.address)
        distance_between_restoraunt_and_order = distance.distance(
            (order_lat, order_lon), (restaurant_lat, restaurant_lon),
        ).km
        restaurants_with_order_distance.append(
            {
                'restaurant': restaurant,
                'order_distance': round(distance_between_restoraunt_and_order, 2),
            }
        )
    return sorted(restaurants_with_order_distance, key=lambda restaurant: restaurant['order_distance'])
    