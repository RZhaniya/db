# Generated by Django 4.1.13 on 2024-11-04 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecom', '0010_adminactionlog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adminactionlog',
            name='action_type',
            field=models.CharField(choices=[('ADD', 'Өнімді Қосу'), ('UPDATE', 'Өнімді Жаңарту'), ('DELETE', 'Өнімді Жою'), ('ORDER_UPDATE', 'Тапсырысты Жаңарту'), ('ORDER_DELETE', 'Тапсырысты Жою')], max_length=20),
        ),
    ]
