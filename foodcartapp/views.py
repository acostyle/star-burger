from django.http import JsonResponse
from django.templatetags.static import static

import phonenumbers
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Order
from .models import OrderedProduct
from .models import Product


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


@api_view(['POST'])
def register_order(request):
    order = request.data
    required_fields = ('firstname', 'lastname', 'phonenumber', 'address')

    missing_fields = [field for field in required_fields if field not in order]
    if missing_fields:
        return Response(
            {'{}'.format(', '.join(missing_fields)): 'Обязательное поле.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    null_fields = [field for field in required_fields if order[field] is None or order[field] == '']
    if null_fields:
        return Response(
            {'{}'.format(', '.join(null_fields)): 'Это поле не может быть пустым.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    phonenumber = phonenumbers.parse(order['phonenumber'])
    if not phonenumbers.is_valid_number(phonenumber):
        return Response(
            {'phonenumber': 'Введен некорректный номер телефона.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if isinstance(order['firstname'], list):
        return Response(
            {'firstname': 'Not a valid string.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        products = order['products']
    except KeyError:
        return Response(
            {'error': 'products: Это поле обязательное!'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if isinstance(products, str):
        return Response(
            {'error': 'products: Ожидался list со значениями, но был получен "str"'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    elif isinstance(products, list) and not products:
        return Response(
            {'error': 'products: Этот список не может быть пустым'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    elif products is None:
        return Response(
            {'error': 'products: Это поле не может быть пустым.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    last_product_id = Product.objects.last().id
    if products[0]['product'] > last_product_id:
        return Response(
            {'error': 'Недопустимый первичный ключ "{}"'.format(products[0]["product"])},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    obj = Order.objects.create(
        first_name = order['firstname'],
        last_name = order['lastname'],
        phone_number = order['phonenumber'],
        delivery_address=order['address']
    )

    for product in order['products']:
        OrderedProduct.objects.create(
            order = obj,
            product = Product.objects.get(id=product['product']),
            quantity = product['quantity'],
        )

    return Response(order)
