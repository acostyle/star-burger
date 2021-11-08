from django.db import transaction
from django.http import JsonResponse
from django.templatetags.static import static

from geopy import distance
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from places.models import Place
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


def get_place_from_coordinates(address, lat, lon):
    if not lat and not lon:
        return Place(lat=lat, lon=lon)

    coordinates = Place.fetch_coordinates(address)

    place, is_created = Place.objects.get_or_create(
        address=address,
        lat=coordinates.lat,
        lon=coordinates.lon,
    )

    return Place(lat=place.lat, lon=place.lon)


def get_available_restaurants_coords_with_needed_products(order):
    products_in_restaurants = RestaurantMenuItem.objects.get_products_in_restaurants().annotate_with_coordinates()
    order_products = order.ordered_products.all()

    restaurants_with_needed_products = []
    for order_product in order_products:
        for product_in_restaurants in products_in_restaurants:
            if product_in_restaurants.product == order_product.product:
                restaurants_with_needed_products.append(
                    [
                        product_in_restaurants.restaurant,
                        product_in_restaurants.restaurant_lat,
                        product_in_restaurants.restaurant_lon,
                    ]
                )
    
    return calculate_distances_to_order(
        restaurants=restaurants_with_needed_products,
        order_address=order.address,
        lat=order.lat,
        lon=order.lon,
    )


def calculate_distances_to_order(order_address, restaurants, lat, lon):
    order_place = get_place_from_coordinates(
        order_address,
        lat=lat,
        lon=lon,
    )

    restaurants_with_order_distance = []
    for restaurant, restaurant_lat, restaurant_lon in restaurants:
        restaurant_place = get_place_from_coordinates(
            address=restaurant.address,
            lat=restaurant_lat,
            lon=restaurant_lon,
        )
        if order_place is None or restaurant_place is None:
            distance_between_restauraunt_and_order = 0
        else:
            distance_between_restauraunt_and_order = distance.distance(
                (order_place.lat, order_place.lon), (restaurant_place.lat, restaurant_place.lon),
            ).km

        restaurants_with_order_distance.append(
            {
                'restaurant': restaurant,
                'order_distance': round(distance_between_restauraunt_and_order, 2),
            }
        )

    return sorted(restaurants_with_order_distance, key=lambda restaurant: restaurant['order_distance'])
    