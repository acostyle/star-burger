from django.db.models.base import Model
from django.http import JsonResponse
from django.templatetags.static import static
from phonenumber_field.modelfields import PhoneNumberField

import phonenumbers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

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


class OrderedProductSerializer(ModelSerializer):
    class Meta:
        model = OrderedProduct
        fields = ['id', 'product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderedProductSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ['id', 'products', 'firstname', 'lastname', 'phonenumber', 'address']


""" def validate(data):
    errors = []
    required_fields = ('firstname', 'lastname', 'phonenumber', 'address')

    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        errors.append(
            {'{}'.format(', '.join(missing_fields)): 'Обязательное поле.'}
            )

    null_fields = [field for field in required_fields if data[field] is None or data[field] == '']
    if null_fields:
        errors.append(
            {'{}'.format(', '.join(null_fields)): 'Это поле не может быть пустым.'}
            )

    phonenumber = phonenumbers.parse(data['phonenumber'])
    if not phonenumbers.is_valid_number(phonenumber):
        errors.append(
            {'phonenumber': 'Введен некорректный номер телефона.'}
            )
    
    if isinstance(data['firstname'], list):
        errors.append(
            {'firstname': 'Not a valid string.'}
            )

    try:
        products = data['products']
    except KeyError:
        errors.append(
            {'error': 'products: Это поле обязательное!'}
            )

    if isinstance(products, str):
        errors.append(
            {'error': 'products: Ожидался list со значениями, но был получен "str"'}
        )
    elif isinstance(products, list) and not products:
        errors.append(
            {'error': 'products: Этот список не может быть пустым'}
        )
    elif products is None:
        errors.append(
            {'error': 'products: Это поле не может быть пустым.'}
        )

    last_product_id = Product.objects.last().id
    if type(products) == list and products[0]['product'] > last_product_id:
        errors.append(
            {'error': 'Недопустимый первичный ключ "{}"'.format(products[0]["product"])}
        )
    
    if errors:
        raise ValidationError(errors) """

@api_view(['POST'])
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    obj = Order.objects.create(
        firstname=serializer.validated_data['firstname'],
        lastname=serializer.validated_data['lastname'],
        phonenumber=serializer.validated_data['phonenumber'],
        address=serializer.validated_data['address']
    )

    for product in serializer.validated_data['products']:
        OrderedProduct.objects.create(
            order = obj,
            product = Product.objects.get(id=product['product']),
            quantity = product['quantity'],
        )

    return Response(serializer.validated_data)
