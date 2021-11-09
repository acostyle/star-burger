from django.contrib import admin
from django.http.response import HttpResponseRedirect
from django.shortcuts import reverse
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.http import url_has_allowed_host_and_scheme

from star_burger import settings
from places.models import Place
from .models import Order
from .models import OrderedProduct
from .models import Product
from .models import ProductCategory
from .models import Restaurant
from .models import RestaurantMenuItem


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


class OrderedProductInline(admin.TabularInline):
    model = OrderedProduct

    fields = ["product", "quantity", "cost"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [
        OrderedProductInline,
    ]

    list_display = [
        "id",
        "firstname",
        "lastname",
        "phonenumber",
    ]

    def response_change(self, request, obj):
        response = super().response_change(request, obj)
        url = request.GET.get("next")

        if not url:
            return response
        
        is_url_safe = url_has_allowed_host_and_scheme(
            url,
            allowed_hosts=settings.ALLOWED_HOSTS,
        )
        if "next" in request.GET and is_url_safe:
            return HttpResponseRedirect(url)
        
        return response

    def save_model(self, request, obj, form, change):
        address = obj.address
        coordinates = Place.fetch_coordinates(address)
        Place.objects.get_or_create(
            address=address,
            lat=coordinates.lat,
            lon=coordinates.lon,
        )

        super().save_model(request, obj, form, change)


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        "name",
        "address",
        "contact_phone",
    ]
    list_display = [
        "name",
        "address",
        "contact_phone",
    ]
    inlines = [RestaurantMenuItemInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "get_image_list_preview",
        "name",
        "category",
        "price",
    ]
    list_display_links = [
        "name",
    ]
    list_filter = [
        "category",
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        "name",
        "category__name",
    ]

    inlines = [RestaurantMenuItemInline]
    fieldsets = (
        (
            "Общее",
            {
                "fields": [
                    "name",
                    "category",
                    "image",
                    "get_image_preview",
                    "price",
                ]
            },
        ),
        (
            "Подробно",
            {
                "fields": [
                    "special_status",
                    "description",
                ],
                "classes": ["wide"],
            },
        ),
    )

    readonly_fields = [
        "get_image_preview",
    ]

    class Media:
        css = {"all": (static("admin/foodcartapp.css"))}

    def get_image_preview(self, obj):
        if not obj.image:
            return "выберите картинку"
        return format_html(
            '<img src="{url}" style="max-height: 200px;"/>', url=obj.image.url
        )

    get_image_preview.short_description = "превью"

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return "нет картинки"
        edit_url = reverse("admin:foodcartapp_product_change", args=(obj.id,))
        return format_html(
            '<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>',
            edit_url=edit_url,
            src=obj.image.url,
        )

    get_image_list_preview.short_description = "превью"


@admin.register(ProductCategory)
class ProductAdmin(admin.ModelAdmin):
    pass
