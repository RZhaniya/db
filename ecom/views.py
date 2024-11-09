from django.shortcuts import render,redirect
from . import forms,models
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
import cyrtranslit

def home_view(request):
    products = models.Product.objects.all()
    categories = models.Product.CATEGORY_CHOICES  # Получаем все категории

    # Инициализируем переменные
    last_ordered_product_id = None
    recommended_products = []  # Начальное значение для рекомендованных товаров

    # Получаем идентификатор последнего заказанного товара
    if request.user.is_authenticated:
        last_order = models.Orders.objects.filter(customer__user=request.user).order_by('-order_date').first()
        if last_order:
            last_ordered_product_id = last_order.product.id
            
            # Получаем рекомендованные товары, исключая последний заказанный
            recommended_products = models.Product.objects.filter(category=last_order.product.category).exclude(id=last_ordered_product_id)

    # Извлечение данных из куки
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter = product_ids.split('|')
        product_count_in_cart = len(set(counter))
    else:
        product_count_in_cart = 0
    
    return render(request, 'ecom/index.html', {
        'products': products,
        'categories': categories,  # Передаем категории в контекст
        'product_count_in_cart': product_count_in_cart,
        'is_staff': request.user.is_staff,  # Передаем статус пользователя в шаблон
        'recommended_products': recommended_products,  # Передаем рекомендованные товары в контекст
        'last_ordered_product_id': last_ordered_product_id,  # Передаем ID последнего заказанного товара
    })

from django.shortcuts import render
from .models import Product

from django.shortcuts import redirect

def category_products(request, category):
    products = Product.objects.filter(category=category)
    
    # check if a product has been added to cart
    if request.method == 'POST':
        pk = request.POST.get('product_id')
        if pk:
            response = redirect('category_products', category=category)
            # add the product id to the cart cookie
            if 'product_ids' in request.COOKIES:
                product_ids = request.COOKIES['product_ids']
                if product_ids == '':
                    product_ids = str(pk)
                else:
                    product_ids = product_ids + '|' + str(pk)
                response.set_cookie('product_ids', product_ids)
            else:
                response.set_cookie('product_ids', pk)
            return response
    
    return render(request, 'ecom/categories.html', {'products': products, 'category': category})

def product_detail_view(request, pk):
    product = Product.objects.get(pk=pk)
    return render(request, 'ecom/product_detail.html', {'product': product})

#for showing login button for admin(by sumit)
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return HttpResponseRedirect('adminlogin')

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.models import Group
from .serializers import UserSerializer, CustomerSerializer


from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib import messages

def customer_signup_view(request):
    userForm = forms.CustomerUserForm()
    customerForm = forms.CustomerForm()
    errors = {}

    if request.method == 'POST':
        userForm = forms.CustomerUserForm(request.POST)
        username = userForm.data.get('username')  # Получаем имя пользователя из данных формы
        
        User = get_user_model()
        
        # Проверка на уникальность username
        if User.objects.filter(username=username).first():
            print("hello1")
            userForm = forms.CustomerUserForm()
            customerForm = forms.CustomerForm()
            messages.error(request, "Пользователь с таким именем уже существует.")
            mydict = {'userForm': userForm, 'customerForm': customerForm, 'errors': errors}
            return render(request, 'ecom/customersignup.html', context=mydict)
        else:
            customerForm = forms.CustomerForm(request.POST, request.FILES)

            if not userForm.is_valid():
                errors.update(userForm.errors)
            
            if not customerForm.is_valid():
                errors.update(customerForm.errors)

            print("User form errors:", userForm.errors)
            print("Customer form errors:", customerForm.errors)
            errors = userForm.errors

            if userForm.is_valid() and customerForm.is_valid():
                user = userForm.save(commit=False)
                user.set_password(user.password)
                user.save()

                customer = customerForm.save(commit=False)
                customer.user = user
                customer.save()

                my_customer_group, created = Group.objects.get_or_create(name='CUSTOMER')
                my_customer_group.user_set.add(user)

                return HttpResponseRedirect('customerlogin')
            
    mydict = {'userForm': userForm, 'customerForm': customerForm, 'errors': errors}
    
    return render(request, 'ecom/customersignup.html', context=mydict)

@api_view(['POST'])
def customer_signup_api_view(request):
    user_serializer = UserSerializer(data=request.data)
    customer_serializer = CustomerSerializer(data=request.data)

    if user_serializer.is_valid() and customer_serializer.is_valid():
        user = user_serializer.save()
        customer = customer_serializer.save(user=user)

        # Добавить пользователя в группу
        my_customer_group, created = Group.objects.get_or_create(name='CUSTOMER')
        my_customer_group.user_set.add(user)

        return Response(user_serializer.data, status=status.HTTP_201_CREATED)
    return Response(
        {
            'user_errors': user_serializer.errors,
            'customer_errors': customer_serializer.errors
        },
        status=status.HTTP_400_BAD_REQUEST
    )

#-----------for checking user iscustomer
def is_customer(user):
    try:
        customer_group = Group.objects.get(name='CUSTOMER')
        return customer_group in user.groups.all()
    except Group.DoesNotExist:
        return False



#---------AFTER ENTERING CREDENTIALS WE CHECK WHETHER USERNAME AND PASSWORD IS OF ADMIN,CUSTOMER
def afterlogin_view(request):
    if is_customer(request.user):
        return redirect('')
    else:
        return redirect('admin-dashboard')

#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    # for cards on dashboard
    customercount=models.Customer.objects.all().count()
    productcount=models.Product.objects.all().count()
    ordercount=models.Orders.objects.all().count()

    # for recent order tables
    orders=models.Orders.objects.all()
    ordered_products=[]
    ordered_bys=[]
    for order in orders:
        ordered_product=models.Product.objects.all().filter(id=order.product.id)
        ordered_by=models.Customer.objects.all().filter(id = order.customer.id)
        ordered_products.append(ordered_product)
        ordered_bys.append(ordered_by)

    mydict={
    'customercount':customercount,
    'productcount':productcount,
    'ordercount':ordercount,
    'data':zip(ordered_products,ordered_bys,orders),
    }
    return render(request,'ecom/admin_dashboard.html',context=mydict)


# admin view customer table
@login_required(login_url='adminlogin')
def view_customer_view(request):
    customers=models.Customer.objects.all()
    return render(request,'ecom/view_customer.html',{'customers':customers})

# admin delete customer
@login_required(login_url='adminlogin')
def delete_customer_view(request,pk):
    customer=models.Customer.objects.get(id=pk)
    user=models.User.objects.get(id=customer.user_id)
    user.delete()
    customer.delete()
    return redirect('view-customer')


@login_required(login_url='adminlogin')
def update_customer_view(request,pk):
    customer=models.Customer.objects.get(id=pk)
    user=models.User.objects.get(id=customer.user_id)
    userForm=forms.CustomerUserForm(instance=user)
    customerForm=forms.CustomerForm(request.FILES,instance=customer)
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST,instance=user)
        customerForm=forms.CustomerForm(request.POST,instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return redirect('view-customer')
    return render(request,'ecom/admin_update_customer.html',context=mydict)

# admin view the product
@login_required(login_url='adminlogin')
def admin_products_view(request):
    products=models.Product.objects.all()
    return render(request,'ecom/admin_products.html',{'products':products})


from .models import AdminActionLog

# admin add product by clicking on floating button
@login_required(login_url='adminlogin')
def admin_add_product_view(request):
    productForm=forms.ProductForm()
    if request.method=='POST':
        productForm=forms.ProductForm(request.POST, request.FILES)
        if productForm.is_valid():
            productForm.save()
            AdminActionLog.objects.create(
                admin_user=request.user,
                action_type='Тауар косу',
                details=f"Тауар косылды: {productForm.instance.name}"  # Или любое другое поле
            )
        return HttpResponseRedirect('admin-products')
    return render(request,'ecom/admin_add_products.html',{'productForm':productForm})


@login_required(login_url='adminlogin')
def delete_product_view(request, pk):
    # Получаем продукт по первичному ключу
    product=models.Product.objects.get(id=pk)
    product_name = product.name

    # Переносим продукт в архив
    archived_product = models.ArchivedProduct(
        name=product.name,
        product_image=product.product_image,
        price=product.price,
        description=product.description,
        is_promoted=product.is_promoted,
        discount_percentage=product.discount_percentage,
        category=product.category,
        manufacturer=product.manufacturer,
        structure=product.structure
    )
    archived_product.save()  # Сохраняем архивированный продукт

    # Удаляем оригинальный продукт
    product.delete()

    # Логируем действие администратора
    AdminActionLog.objects.create(
        admin_user=request.user,
        action_type='Тауар жою',
        details=f"Жойылган тауар: {product_name}"
    )
    
    return redirect('admin-products')

def archived_products_view(request):
    archived_products = models.ArchivedProduct.objects.all()
    return render(request, 'ecom/admin_archived_products.html', {'products': archived_products})


@login_required(login_url='adminlogin')
def update_product_view(request, pk):
    print(f"Received request to update product with id: {pk}")
    
    # Получаем продукт по id и проверяем его существование
    product = models.Product.objects.get(id=pk)
    print(f"Fetched product: {product}")
    
    productForm = forms.ProductForm(instance=product)
    
    if request.method == 'POST':
        print("POST request received.")
        print(f"POST data: {request.POST}")
        print(f"FILES data: {request.FILES}")
        
        # Заполняем форму с данными из запроса
        productForm = forms.ProductForm(request.POST, request.FILES, instance=product)
        
        if productForm.is_valid():
            print("Form is valid. Saving product...")
            productForm.save()
            AdminActionLog.objects.create(
                admin_user=request.user,
                action_type='Ондеу',
                details=f"Онделген тауар: {productForm.instance.name}"
            )
            print("Product updated successfully.")
            return redirect('admin-products')
        else:
            print("Form is invalid.")
            print(f"Form errors: {productForm.errors}")

    return render(request, 'ecom/admin_update_product.html', {'productForm': productForm})



@login_required(login_url='adminlogin')
def admin_view_booking_view(request):
    orders=models.Orders.objects.all()
    ordered_products=[]
    ordered_bys=[]
    for order in orders:
        ordered_product=models.Product.objects.all().filter(id=order.product.id)
        ordered_by=models.Customer.objects.all().filter(id = order.customer.id)
        ordered_products.append(ordered_product)
        ordered_bys.append(ordered_by)
    return render(request,'ecom/admin_view_booking.html',{'data':zip(ordered_products,ordered_bys,orders)})


@login_required(login_url='adminlogin')
def delete_order_view(request,pk):
    order=models.Orders.objects.get(id=pk)
    order_id = order.id  # Получаем ID заказа для логирования
    order.delete()
    AdminActionLog.objects.create(
        admin_user=request.user,
        action_type='Тапсырыс жою',
        details=f"Жойылган тапсырыс: {order_id}"
    )
    return redirect('admin-view-booking')

# for changing status of order (pending,delivered...)
@login_required(login_url='adminlogin')
def update_order_view(request,pk):
    order=models.Orders.objects.get(id=pk)
    orderForm=forms.OrderForm(instance=order)
    if request.method=='POST':
        orderForm=forms.OrderForm(request.POST,instance=order)
        if orderForm.is_valid():
            orderForm.save()
            AdminActionLog.objects.create(
                admin_user=request.user,
                action_type='Тапсырыс ондеу',
                details=f"Онделген тапсырыс: {order.id}, жана мартебеси: {orderForm.cleaned_data['status']}"
            )
            return redirect('admin-view-booking')
    return render(request,'ecom/update_order.html',{'orderForm':orderForm})

@login_required(login_url='adminlogin')
def admin_action_log_view(request):
    logs = AdminActionLog.objects.all().order_by('-timestamp')
    return render(request, 'ecom/admin_action_log.html', {'logs': logs})


# admin view the feedback
@login_required(login_url='adminlogin')
def view_feedback_view(request):
    feedbacks=models.Feedback.objects.all()
    return render(request,'ecom/view_feedback.html',{'feedbacks':feedbacks})












#---------------------------------------------------------------------------------
#------------------------ PUBLIC CUSTOMER RELATED VIEWS START ---------------------
#---------------------------------------------------------------------------------
from transliterate import translit
from django.db.models import Q
from urllib.parse import quote, unquote
from django.urls import reverse
from unidecode import unidecode

# for product in models.Product.objects.all():
#     product.s_name = unidecode(product.name)
#     product.s_description = unidecode(product.description)
#     product.save()

def search_view(request):
    # Get the search query from the request
    query = request.GET.get('query', '').strip()
    original = query;
    # print(query)
    # query = unquote(query)
    query = unidecode(query)
    # print(query)
    # Use the query to filter the products
    products = models.Product.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(s_name__icontains=query) |
        Q(s_description__icontains=query)
    )
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0

    # word variable will be shown in html when user click on search button
    word = f"Іздеу нәтижелері '{original}':"

    if request.user.is_authenticated:
        return render(request,'ecom/customer_home.html',{'products':products,'word':word,'product_count_in_cart':product_count_in_cart})
    return render(request,'ecom/index.html',{'products':products,'word':word,'product_count_in_cart':product_count_in_cart})


# any one can add product to cart, no need of signin
from django.urls import reverse

def add_to_cart_view(request,pk):
    products=models.Product.objects.all()
    categories = models.Product.CATEGORY_CHOICES

    #for cart counter, fetching products ids added by customer from cookies
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=1

    category_pk = request.GET.get('category_pk')
    print(category_pk)
    if category_pk:
        response = render(request, 'ecom/categories.html',{'products':products,'categories': categories, 'product_count_in_cart':product_count_in_cart})
    else:
        response = render(request, 'ecom/index.html',{'products':products,'categories': categories, 'product_count_in_cart':product_count_in_cart})

    #adding product id to cookies
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids=="":
            product_ids=str(pk)
        else:
            product_ids=product_ids+"|"+str(pk)
        response.set_cookie('product_ids', product_ids)
    else:
        response.set_cookie('product_ids', pk)

    product=models.Product.objects.get(id=pk)

    if category_pk:
        return redirect('category_products', category_pk=category_pk)

    return response





# for checkout of cart
def cart_view(request):
    #for cart counter
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0

    # fetching product details from db whose id is present in cookie
    products=None
    total=0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_id_in_cart=product_ids.split('|')
            products=models.Product.objects.all().filter(id__in = product_id_in_cart)

            #for total price shown in cart
            for p in products:
                total=total+p.price
    return render(request,'ecom/cart.html',{'products':products,'total':total,'product_count_in_cart':product_count_in_cart})


def remove_from_cart_view(request,pk):
    #for counter in cart
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0

    # removing product id from cookie
    total=0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        product_id_in_cart=product_ids.split('|')
        product_id_in_cart=list(set(product_id_in_cart))
        product_id_in_cart.remove(str(pk))
        products=models.Product.objects.all().filter(id__in = product_id_in_cart)
        #for total price shown in cart after removing product
        for p in products:
            total=total+p.price

        #  for update coookie value after removing product id in cart
        value=""
        for i in range(len(product_id_in_cart)):
            if i==0:
                value=value+product_id_in_cart[0]
            else:
                value=value+"|"+product_id_in_cart[i]
        response = render(request, 'ecom/cart.html',{'products':products,'total':total,'product_count_in_cart':product_count_in_cart})
        if value=="":
            response.delete_cookie('product_ids')
        response.set_cookie('product_ids',value)
        return response


def send_feedback_view(request):
    feedbackForm=forms.FeedbackForm()
    if request.method == 'POST':
        feedbackForm = forms.FeedbackForm(request.POST)
        if feedbackForm.is_valid():
            feedbackForm.save()
            return render(request, 'ecom/feedback_sent.html')
    return render(request, 'ecom/send_feedback.html', {'feedbackForm':feedbackForm})


#---------------------------------------------------------------------------------
#------------------------ CUSTOMER RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------


def customer_home_view(request):
    products = models.Product.objects.all()
    categories = models.Product.CATEGORY_CHOICES
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0
    return render(request,'ecom/customer_home.html',{'products':products,'categories': categories, 'product_count_in_cart':product_count_in_cart})



# shipment address before placing order
@login_required(login_url='customerlogin')
def customer_address_view(request):
    # this is for checking whether product is present in cart or not
    # if there is no product in cart we will not show address form
    product_in_cart=False
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_in_cart=True
    #for counter in cart
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0

    addressForm = forms.AddressForm()
    if request.method == 'POST':
        addressForm = forms.AddressForm(request.POST)
        if addressForm.is_valid():
            # here we are taking address, email, mobile at time of order placement
            # we are not taking it from customer account table because
            # these thing can be changes
            email = addressForm.cleaned_data['Email']
            mobile = addressForm.cleaned_data['Mobile']
            address = addressForm.cleaned_data['Address']
            address = cyrtranslit.to_latin(address, 'ru')
            #for showing total price on payment page.....accessing id from cookies then fetching  price of product from db
            total=0
            if 'product_ids' in request.COOKIES:
                product_ids = request.COOKIES['product_ids']
                if product_ids != "":
                    product_id_in_cart=product_ids.split('|')
                    products=models.Product.objects.all().filter(id__in = product_id_in_cart)
                    for p in products:
                        total=total+p.price

            response = render(request, 'ecom/payment.html',{'total':total})
            response.set_cookie('email',email)
            response.set_cookie('mobile',mobile)
            response.set_cookie('address',address)
            return response
    return render(request,'ecom/customer_address.html',{'addressForm':addressForm,'product_in_cart':product_in_cart,'product_count_in_cart':product_count_in_cart})



# here we are just directing to this view...actually we have to check whther payment is successful or not
#then only this view should be accessed
@login_required(login_url='customerlogin')
def payment_success_view(request):
    # Here we will place order | after successful payment
    # we will fetch customer  mobile, address, Email
    # we will fetch product id from cookies then respective details from db
    # then we will create order objects and store in db
    # after that we will delete cookies because after order placed...cart should be empty
    customer=models.Customer.objects.get(user_id=request.user.id)
    products=None
    email=None
    mobile=None
    address=None
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_id_in_cart=product_ids.split('|')
            products=models.Product.objects.all().filter(id__in = product_id_in_cart)
            # Here we get products list that will be ordered by one customer at a time

    # these things can be change so accessing at the time of order...
    if 'email' in request.COOKIES:
        email=request.COOKIES['email']
    if 'mobile' in request.COOKIES:
        mobile=request.COOKIES['mobile']
    if 'address' in request.COOKIES:
        address=request.COOKIES['address']

    # here we are placing number of orders as much there is a products
    # suppose if we have 5 items in cart and we place order....so 5 rows will be created in orders table
    # there will be lot of redundant data in orders table...but its become more complicated if we normalize it
    for product in products:
        models.Orders.objects.get_or_create(customer=customer,product=product,status='Растауды кутуде',email=email,mobile=mobile,address=address)

    # after order placed cookies should be deleted
    response = render(request,'ecom/payment_success.html')
    response.delete_cookie('product_ids')
    response.delete_cookie('email')
    response.delete_cookie('mobile')
    response.delete_cookie('address')
    return response




@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def my_order_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    orders=models.Orders.objects.all().filter(customer_id = customer)
    ordered_products=[]
    for order in orders:
        ordered_product=models.Product.objects.all().filter(id=order.product.id)
        ordered_products.append(ordered_product)

    return render(request,'ecom/my_order.html',{'data':zip(ordered_products,orders)})




#--------------for discharge patient bill (pdf) download and printing
import io
import os
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result, encoding='UTF-8')
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return
def fetch_resources(uri, rel):
    path = os.path.join(settings.MEDIA_ROOT, uri.replace
    (settings.MEDIA_URL, ""))
    return path 




@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def download_invoice_view(request,orderID,productID):
    order=models.Orders.objects.get(id=orderID)
    product=models.Product.objects.get(id=productID)
    name = cyrtranslit.to_latin(product.name, 'ru')
    description = cyrtranslit.to_latin(product.description, 'ru')
    status = cyrtranslit.to_latin(order.status, 'ru')
    mydict={
        'orderDate':order.order_date, 
        'customerName':request.user,
        'customerEmail':order.email,
        'customerMobile':order.mobile,
        'shipmentAddress':order.address,
        'orderStatus':status,

        'productName':name,
        'productImage':product.product_image,
        'productPrice':product.price,
        'productDescription':description,


    }
    return render_to_pdf('ecom/download_invoice.html',mydict)






@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def my_profile_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    return render(request,'ecom/my_profile.html',{'customer':customer})


@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def edit_profile_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    user=models.User.objects.get(id=customer.user_id)
    userForm=forms.CustomerUserForm(instance=user)
    customerForm=forms.CustomerForm(request.FILES,instance=customer)
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST,instance=user)
        customerForm=forms.CustomerForm(request.POST,instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return HttpResponseRedirect('my-profile')
    return render(request,'ecom/edit_profile.html',context=mydict)









#---------------------------------------------------------------------------------
#------------------------ ABOUT US AND CONTACT US VIEWS START --------------------
#---------------------------------------------------------------------------------
def aboutus_view(request):
    return render(request,'ecom/aboutus.html')
