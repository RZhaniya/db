from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Customer(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    profile_pic= models.ImageField(upload_to='profile_pic/CustomerProfilePic/',null=True,blank=True, default="profile_pic/CustomerProfilePic/default.jpg")
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20,null=False)
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_id(self):
        return self.user.id
    def __str__(self):
        return self.user.first_name

from unidecode import unidecode

class Product(models.Model):
    CATEGORY_CHOICES = (
        ('drugs', 'Дәрілік заттар'),
        ('vitamins', 'Витаминдер мен диеталық қоспалар'),
        ('medical', 'Медициналық мақсаттағы бұйымдар'),
        ('mother', 'Ана мен бала'),
        ('medtech', 'Медициналық техника'),
        ('cosmetics', 'Косметика'),
        ('hygiene', 'Гигиена'),
    )

    name = models.CharField(max_length=40)
    product_image = models.ImageField(upload_to='product_image/', null=True, blank=True, default="profile_pic/CustomerProfilePic/default.jpg")
    price = models.PositiveIntegerField()
    description = models.CharField(max_length=40)
    s_name = models.CharField(max_length=40, blank=True)
    s_description = models.CharField(max_length=40, blank=True)
    is_promoted = models.BooleanField(default=False)
    discount_percentage = models.PositiveIntegerField(default=0, blank=True, null=True)
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES, default="uncategorized")
    manufacturer = models.CharField(max_length=100, default="Белгісіз")
    structure = models.CharField(max_length=100, default="Белгісіз", null=True, blank=True)


    def save(self, *args, **kwargs):
        self.s_name = unidecode(self.name)
        self.s_description = unidecode(self.description)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def discounted_price(self):
        if self.is_promoted:
            return int(self.price * (100 - self.discount_percentage) / 100)
        return self.price



class Orders(models.Model):
    STATUS =(
        ('Растауды кутуде','Растауды кутуде'),
        ('Тапсырыс расталды','Тапсырыс расталды'),
        ('Жеткізуге дайын','Жеткізуге дайын'),
        ('Жеткізілді','Жеткізілді'),
    )
    customer=models.ForeignKey('Customer', on_delete=models.CASCADE,null=True)
    product=models.ForeignKey('Product',on_delete=models.CASCADE,null=True)
    email = models.CharField(max_length=50,null=True)
    address = models.CharField(max_length=500,null=True)
    mobile = models.CharField(max_length=20,null=True)
    order_date= models.DateField(auto_now_add=True,null=True)
    status=models.CharField(max_length=50,null=True,choices=STATUS)


class Feedback(models.Model):
    name=models.CharField(max_length=40)
    feedback=models.CharField(max_length=500)
    date= models.DateField(auto_now_add=True,null=True)
    def __str__(self):
        return self.name

class AdminActionLog(models.Model):
    ACTION_TYPES = [
        ('ADD', 'Өнімді Қосу'),
        ('UPDATE', 'Өнімді Жаңарту'),
        ('DELETE', 'Өнімді Жою'),
        ('ORDER_UPDATE', 'Тапсырысты Жаңарту'),
        ('ORDER_DELETE', 'Тапсырысты Жою'),
    ]

    admin_user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField()

    def __str__(self):
        return f"{self.admin_user.username} - {self.action_type} at {self.timestamp}"
    

class ArchivedProduct(models.Model):
    name = models.CharField(max_length=40)
    product_image = models.ImageField(upload_to='product_image/', null=True, blank=True, default="profile_pic/CustomerProfilePic/default.jpg")
    price = models.PositiveIntegerField()
    description = models.CharField(max_length=40)
    s_name = models.CharField(max_length=40, blank=True)
    s_description = models.CharField(max_length=40, blank=True)
    is_promoted = models.BooleanField(default=False)
    discount_percentage = models.PositiveIntegerField(default=0, blank=True, null=True)
    category = models.CharField(max_length=40)  # Возможно, стоит добавить выбор категорий
    manufacturer = models.CharField(max_length=100, default="Белгісіз")
    structure = models.CharField(max_length=100, default="Белгісіз", null=True, blank=True)
    archived_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.s_name = unidecode(self.name)
        self.s_description = unidecode(self.description)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name