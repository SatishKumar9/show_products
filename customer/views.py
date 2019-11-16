from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from customer.forms import CustomerCreationForm, Contact_Form, UpdateProfile
from vendor.models import Category, Product, Review, VendorProfile, VendorQty
from vendor.forms import writereview
from cart.models import Order
from customer.models import CustomerProfile
from django.contrib.auth.decorators import login_required

import requests, json
from customer.forms import TournamentJoin


def get_user_order(request):
    user_profile = get_object_or_404(CustomerProfile, Customer=request.user)
    ord = Order.objects.filter(owner=user_profile, is_ordered=True)
    if ord.exists():
        return ord
    return 0


def index(request):
    return render(request, 'customer/base.html')


def QrCode(request, id):
    This_Order = get_object_or_404(Order, id=id)
    string = This_Order.get_qr_code()
    context = {
        "string": string,
    }
    return render(request, "customer/QrCode.html", context)


@login_required
def profile(request):
    a = request.user
    # print(a)
    customer = CustomerProfile.objects.get(Customer=a)
    if request.method == 'POST':
        form = UpdateProfile(request.POST, instance=a)
        ContactForm = Contact_Form(request.POST, instance=customer)
        if form.is_valid() and ContactForm.is_valid():
            PhNo = ContactForm.cleaned_data.get('phone_number')
            addr = ContactForm.cleaned_data.get('address')
            user = form.save(commit=False)
            user.save()

            customer.phone_number = PhNo
            customer.address = addr
            customer.save()
            return redirect('customer:home')
    else:
        form = UpdateProfile(instance=request.user)
        ContactForm = Contact_Form(instance=customer)
        placed_order = get_user_order(request)
        context = {
            'form': form,
            'ContactForm': ContactForm,
            'ordre': placed_order
        }
        return render(request, 'customer/profile.html', context)


def itemsview(request, pk):
    categories = Category.objects.all()
    cat = Category.objects.get(id=pk)
    current_order_products = []
    if request.user.is_authenticated:
        filtered_orders = Order.objects.filter(owner=request.user.cus, is_ordered=False)
        if filtered_orders.exists():
            user_order = filtered_orders[0]
            user_order_items = user_order.items.all()
            current_order_products = [product.product for product in user_order_items]

    context = {
        'categories': categories,
        'cat': cat,
        'current_order_products': current_order_products
    }

    return render(request, "customer/items.html", context)


def Search_Results(request):
    products = []
    current_order_products = []
    query = request.GET.get('q')
    # print(query)
    if query:
        products = Product.objects.filter(
            Q(prod_name__icontains=query) |
            Q(brand__icontains=query) |
            Q(category__cat_name__contains=query)
        )
    if request.user.is_authenticated:
        filtered_orders = Order.objects.filter(owner=request.user.cus)
        if filtered_orders.exists():
            user_order = filtered_orders[0]
            user_order_items = user_order.items.all()
            current_order_products = [product.product for product in user_order_items]
    context = {
        "products": products,
        "current_order_products": current_order_products,
    }
    return render(request, 'customer/search_results.html', context)


def list_categories(request):
    url = 'http://127.0.0.1:8000/shopping/categories_list'
    response = requests.get(url)
    categories = response.json()

    for category in categories:
        if not Category.objects.filter(cat_name=category['cat_name']).exists():
            c = Category.objects.create(cat_name=category['cat_name'])
            c.save()

    all_categories = Category.objects.all()
    is_vendor = False
    if request.user.is_authenticated:
        try:
            vendor = request.user.vendorprofile
            is_vendor = True
        except:
            pass
    context = {
        "is_vendor": is_vendor,
        'categories': all_categories,
    }
    return render(request, 'customer/index.html', context)


def customer_signup(request):
    if request.method == 'POST':
        form = CustomerCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            contact_number = form.cleaned_data['contact_number']
            c = CustomerProfile.objects.get(Customer=user)
            c.phone_number = contact_number
            login(request, user)
            return redirect('customer:home')
    else:
        form = CustomerCreationForm()
    return render(request, 'customer/signup.html', {'form': form})


def customer_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
                return redirect('customer:home')
    else:
        form = AuthenticationForm
    return render(request, 'customer/login.html', {'form': form})


@login_required
def customer_logout(request):
    logout(request)
    return render(request, 'customer/logout.html')


def forgot_pass(request):
    return render(request, 'registration/password_reset_form.html')


def itemdetailview(request, pk, ck):
    categories = Category.objects.all()
    cat = Category.objects.get(id=pk)
    prod = Product.objects.get(id=ck)
    products = Product.objects.filter(category=cat)
    all_vendors = VendorQty.objects.filter(product=prod)
    current_order_products = []
    if request.user.is_authenticated:
        filtered_orders = Order.objects.filter(owner=request.user.cus, is_ordered=False)
        if filtered_orders.exists():
            user_order = filtered_orders[0]
            user_order_items = user_order.items.all()
            current_order_products = [product.product for product in user_order_items]
    context = {
        'categories': categories,
        'cat': cat,
        'prod': prod,
        'vendors': all_vendors,
        'current_order_products': current_order_products,
    }
    return render(request, "customer/itemdetail.html", context)


def faq(request):
    return render(request, 'customer/faqs.html')


def about_us(request):
    return render(request, 'customer/about_us.html')


@login_required
def reviewtext(request, categ, product):
    prod = get_object_or_404(Product, pk=product)
    cat = get_object_or_404(Category, pk=categ)
    if request.method == 'POST':
        form = writereview(request.POST)
        if form.is_valid():
            content = request.POST.get('content')
            rating = request.POST.get('rating')
            review1 = Review.objects.create(category=cat, product=prod, customer=request.user, content=content,
                                            rating=rating)
            review1.save()
            return redirect('/customer/home/' + str(categ) + '/' + str(product) + '/')
    else:
        form = writereview()
    return render(request, 'customer/writereview.html', {'form': form})


def get_details(request):
    url = 'http://127.0.0.1:8000/api/tournaments/'
    response = requests.get(url)

    tournaments = response.json()
    return render(request, 'customer/get_details.html', {'tournaments': tournaments})


def join_tournament(request, pk):
    if request.method == 'POST':
        form = TournamentJoin(request.POST)
        if form.is_valid():
            url = 'http://127.0.0.1:8000/api/tournaments_join/'
            k = request.POST['pk']
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            if form.cleaned_data['phone_number']:
                phone_num = form.cleaned_data['phone_number']
                data = json.dumps({'name': name, 'tournament': k, 'mail': email, 'phoneNumber': phone_num})
                requests.post(url=url, data=data)

            else:
                data = json.dumps({'name': name, 'tournament': k, 'mail': email})
                requests.post(url=url, data=data)
            return redirect('customer:get_tournament_details')

        else:
            print('form is invalid')
            print(form.errors)
    else:
        form = TournamentJoin()

    # print(int(pk))
    return render(request, 'customer/submit_tournament_details.html', {'form': form, 'pk': int(pk)})


def show_products_api(request):
    url = 'http://127.0.0.1:8000/shopping/product_list'
    response = requests.get(url)
    products = response.json()

    for product in products:
        c = Category.objects.get(cat_name=product['category'])
        p = Product.objects.create(category=c, prod_name=product['prod_name'],
                                   description=product['description'],
                                   stock=product['stock'], cost=product['cost'],
                                   brand=product['brand'])
        p.save()

        u = User.objects.get(username='sportshub')
        vendor = VendorQty.objects.get_or_create(Vendor=u, product=p)[0]
        vendor.qty = product['stock']
        vendor.save()

    return render(request, 'customer/show_products_api.html', {'products': products})
