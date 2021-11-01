# Generated by Django 3.2 on 2021-11-01 13:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0040_orderedproduct_cost'),
    ]

    def count_cost_for_old_orders(apps, schema_editor):
        Order = apps.get_model('foodcartapp', 'Order')

        orders = Order.objects.all()
        for order in orders:
            order_products = order.ordered_products.all()
            for order_product in order_products:
                order_product.cost = order_product.quantity * order_product.product.price
                order_product.save()

    operations = [
        migrations.RunPython(count_cost_for_old_orders),
    ]