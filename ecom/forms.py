from django import forms
from django.contrib.auth.models import User
from . import models
from django.core.exceptions import ValidationError
import re


class CustomerUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }
    def clean_username(self):
        # Отключить проверку уникальности
        return self.cleaned_data['username']
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        
        # Проверка длины пароля
        if len(password) < 8:
            raise ValidationError("Пароль должен быть не менее 8 символов.")
        
        # Проверка на наличие заглавной буквы
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Пароль должен содержать хотя бы одну заглавную букву.")
        
        # Проверка на наличие строчной буквы
        if not re.search(r'[a-z]', password):
            raise ValidationError("Пароль должен содержать хотя бы одну строчную букву.")
        
        # Проверка на наличие цифры
        if not re.search(r'\d', password):
            raise ValidationError("Пароль должен содержать хотя бы одну цифру.")
        
        # Проверка на наличие специального символа
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("Пароль должен содержать хотя бы один специальный символ.")

        return password
        
class CustomerForm(forms.ModelForm):
    class Meta:
        model=models.Customer
        fields=['address','mobile','profile_pic']

class ProductForm(forms.ModelForm):
    class Meta:
        model = models.Product
        fields = ['name', 'product_image', 'price', 'description', 'category', 'manufacturer', 'structure', 'is_promoted', 'discount_percentage']
        widgets = {
            'is_promoted': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100, 'step': 5}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'structure': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    is_promoted = forms.BooleanField(required=False, label='Is Promoted?')
    discount_percentage = forms.IntegerField(required=False, label='Discount Percentage (%)')
    category = forms.ChoiceField(choices=models.Product.CATEGORY_CHOICES, label='Category')
    manufacturer = forms.CharField(required=False, label='Manufacturer')



#address of shipment
class AddressForm(forms.Form):
    Email = forms.EmailField()
    Mobile= forms.IntegerField()
    Address = forms.CharField(max_length=500)

class FeedbackForm(forms.ModelForm):
    class Meta:
        model=models.Feedback
        fields=['name','feedback']

#for updating status of order
class OrderForm(forms.ModelForm):
    class Meta:
        model=models.Orders
        fields=['status']

#for contact us page
class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30)
    Email = forms.EmailField()
    Message = forms.CharField(max_length=500,widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}))
