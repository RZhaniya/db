# Generated by Django 4.1.7 on 2023-04-02 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecom', '0003_product_discount_percentage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='discount_percentage',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
    ]
