# Generated by Django 3.2 on 2021-10-14 02:11

from django.db import migrations


def count_cost_for_old_orders(apps, schema_editor):
    OrderedProduct = apps.get_model('foodcartapp', 'OrderedProduct')
    ordered_products = OrderedProduct.objects.all().iterator()
    for ordered_product in ordered_products:
        if not ordered_product:
            ordered_product.cost = ordered_product.product.price * ordered_products.quantity
            ordered_product.save()



class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0040_orderedproduct_cost'),
    ]

    operations = [
        migrations.RunPython(count_cost_for_old_orders),
    ]
