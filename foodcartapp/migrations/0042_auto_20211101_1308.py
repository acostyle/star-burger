# Generated by Django 3.2 on 2021-11-01 13:08

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0041_auto_20211101_1307'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='called_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='дата звонка'),
        ),
        migrations.AddField(
            model_name='order',
            name='commentary',
            field=models.TextField(blank=True, verbose_name='комментарий'),
        ),
        migrations.AddField(
            model_name='order',
            name='delivered_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='дата доставки'),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('cash', 'Наличные'), ('card', 'Карта'), ('not specified', 'Не указано')], db_index=True, default='not specified', max_length=16, verbose_name='способ оплаты'),
        ),
        migrations.AddField(
            model_name='order',
            name='registrated_at',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='дата регистрации'),
        ),
        migrations.AddField(
            model_name='order',
            name='restaurant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='foodcartapp.restaurant', verbose_name='забрать в ресторане'),
        ),
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('processed', 'Обработанный'), ('unprocessed', 'Необработанный')], db_index=True, default='unprocessed', max_length=12, verbose_name='статус заказа'),
        ),
        migrations.AlterField(
            model_name='order',
            name='phonenumber',
            field=phonenumber_field.modelfields.PhoneNumberField(db_index=True, max_length=128, region=None, verbose_name='номер телефона'),
        ),
        migrations.AlterField(
            model_name='orderedproduct',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ordered_products', to='foodcartapp.order', verbose_name='заказ'),
        ),
        migrations.AlterField(
            model_name='orderedproduct',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ordered_products', to='foodcartapp.product', verbose_name='продукт'),
        ),
    ]
