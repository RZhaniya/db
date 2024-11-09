# Generated by Django 4.1.13 on 2024-11-04 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecom', '0011_alter_adminactionlog_action_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArchivedProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('product_image', models.ImageField(blank=True, default='profile_pic/CustomerProfilePic/default.jpg', null=True, upload_to='product_image/')),
                ('price', models.PositiveIntegerField()),
                ('description', models.CharField(max_length=40)),
                ('s_name', models.CharField(blank=True, max_length=40)),
                ('s_description', models.CharField(blank=True, max_length=40)),
                ('is_promoted', models.BooleanField(default=False)),
                ('discount_percentage', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('category', models.CharField(max_length=40)),
                ('manufacturer', models.CharField(default='Белгісіз', max_length=100)),
                ('structure', models.CharField(blank=True, default='Белгісіз', max_length=100, null=True)),
                ('archived_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='is_archived',
            field=models.BooleanField(default=False),
        ),
    ]