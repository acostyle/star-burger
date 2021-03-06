# Generated by Django 3.2 on 2021-11-09 15:44

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0050_delete_orderedproductcost'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderedproduct',
            name='cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Стоимость'),
            preserve_default=False,
        ),
    ]
