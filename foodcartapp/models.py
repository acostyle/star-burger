from django.db import models
from django.db.models import Sum, F
from django.core.validators import MinValueValidator
from django.db.models.expressions import OuterRef, Subquery
from django.utils import timezone

from phonenumber_field.modelfields import PhoneNumberField

from places.models import Place


class RestaurantMenuItemQuerySet(models.QuerySet):
    def get_products_in_restaurants(self):
        return self.select_related('restaurant', 'product').filter(availability=True)

    def annotate_with_coordinates(self):
        place = Place.objects.filter(address=OuterRef('restaurant__address'))
        return self.annotate(
            restaurant_lon=Subquery(
                place.values('lon')
            ),
            restaurant_lat=Subquery(
                place.values('lat')
            ),
        )


class OrderQuerySet(models.QuerySet):
    def count_order_cost(self):
        return self.annotate(
            total_cost=Sum(
                F("ordered_products__cost"),
            )
        )
    
    def receive_orders_in_processing(self):
        orders = self.exclude(status='CLOSED')
        return orders
    
    def annotate_with_coordinates(self):
        place = Place.objects.filter(address=OuterRef('address'))
        return self.annotate(
            lon=Subquery(
                place.values('lon')
            ),
            lat=Subquery(
                place.values('lat')
            )
        )


class OrderedProduct(models.Model):
    product = models.ForeignKey(
        "Product",
        related_name="ordered_products",
        on_delete=models.CASCADE,
        verbose_name="продукт",
    )
    order = models.ForeignKey(
        "Order",
        related_name="ordered_products",
        on_delete=models.CASCADE,
        verbose_name="заказ",
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], verbose_name="количество"
    )
    cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Стоимость",
    )

    class Meta:
        verbose_name = "продукт заказа"
        verbose_name_plural = "продукт заказов"

    def __str__(self):
        return "{0} {1} {2}".format(
            self.product.name,
            self.quantity,
            self.order,
        )


class Restaurant(models.Model):
    name = models.CharField("название", max_length=50)
    address = models.CharField(
        "адрес",
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        "контактный телефон",
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = "ресторан"
        verbose_name_plural = "рестораны"

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = RestaurantMenuItem.objects.filter(availability=True).values_list(
            "product"
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField("название", max_length=50)

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "категории"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField("название", max_length=50)
    category = models.ForeignKey(
        ProductCategory,
        verbose_name="категория",
        related_name="products",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        "цена", max_digits=8, decimal_places=2, validators=[MinValueValidator(0)]
    )
    image = models.ImageField("картинка")
    special_status = models.BooleanField(
        "спец.предложение",
        default=False,
        db_index=True,
    )
    description = models.TextField(
        "описание",
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "товары"

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name="menu_items",
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="menu_items",
        verbose_name="продукт",
    )
    availability = models.BooleanField("в продаже", default=True, db_index=True)
    
    objects = RestaurantMenuItemQuerySet.as_manager()

    class Meta:
        verbose_name = "пункт меню ресторана"
        verbose_name_plural = "пункты меню ресторана"
        unique_together = [
            ["restaurant", "product"]
        ]

    def __str__(self):
        return "{0} - {1}".format(
            self.restaurant.name,
            self.product.name,
        )


class Order(models.Model):
    PROCESSED = "processed"
    UNPROCESSED = "unprocessed"
    ORDER_STATUS_CHOICES = [
        (PROCESSED, "Обработанный"),
        (UNPROCESSED, "Необработанный"),
    ]

    CASH = "cash"
    CARD = "card"
    NOT_SPECIFIED = "not specified"
    ORDER_PAYMENT_METHOD_CHOICES = [
        (CASH, "Наличные"),
        (CARD, "Карта"),
        (NOT_SPECIFIED, "Не указано")
    ]

    firstname = models.CharField(max_length=64, verbose_name="имя")
    lastname = models.CharField(max_length=64, verbose_name="фамилия")
    phonenumber = PhoneNumberField(db_index=True, verbose_name="номер телефона")
    address = models.CharField(max_length=256, verbose_name="адрес доставки")

    status = models.CharField(
        max_length=12,
        choices=ORDER_STATUS_CHOICES,
        default=UNPROCESSED,
        db_index=True,
        verbose_name="статус заказа",
    )
    commentary = models.TextField(
        blank=True, verbose_name="комментарий"
    )
    payment_method = models.CharField(
        max_length=16,
        choices=ORDER_PAYMENT_METHOD_CHOICES,
        default=NOT_SPECIFIED,
        db_index=True,
        verbose_name="способ оплаты",    
    )

    registrated_at = models.DateTimeField(
        db_index=True, default=timezone.now, verbose_name="дата регистрации"
    )
    called_at = models.DateTimeField(
        db_index=True, 
        null=True, 
        blank=True, 
        verbose_name="дата звонка"
    )
    delivered_at = models.DateTimeField(
        db_index=True, null=True, blank=True, verbose_name="дата доставки"
    )

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.SET_NULL,
        verbose_name="забрать в ресторане",
        related_name="orders",
        null=True,
        blank=True,
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = "заказ клиента"
        verbose_name_plural = "заказы клиентов"

    def __str__(self):
        return '{0} {1}'.format(self.firstname, self.address)
