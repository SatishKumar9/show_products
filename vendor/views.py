from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from cart.models import Order
from vendor.forms import ProductsAdd, AddExisting, AddNew, VendorForm
from vendor.models import Product, Category, VendorQty
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from show_products.decorators import vendor_required


def index(request):
    return render(request, 'vendor/base.html')


# def itemsview(request, pk):
#     cat = Category.objects.get(id=pk)
#     current_order_products = []
#     if request.user.is_authenticated:
#         filtered_orders = Order.objects.filter(owner=request.user.cus, is_ordered=False)
#         if filtered_orders.exists():
#             user_order = filtered_orders[0]
#             user_order_items = user_order.items.all()
#             current_order_products = [product.product for product in user_order_items]
#
#     context = {
#         'cat': cat,
#         'current_order_products': current_order_products
#     }
#
#     return render(request, "customer/items.html", context)


def list_categories(request):
    categories = Category.objects.all()
    return render(request, 'customer/index.html', {'categories': categories})


# @login_required(login_url='vendor:actor_authentication:login_all')
# @vendor_required
# def add_products(request):
#     if request.method == 'POST':
#         form = ProductsAdd(request.POST, request.FILES)
#         if form.is_valid():
#             a = form.save()
#             profile = VendorQty.objects.get_or_create(Vendor=request.user, product=a)[0]
#             profile.qty = form.cleaned_data['quantity']
#             profile.save()
#             return redirect('vendor:view_products')
#
#     form = ProductsAdd()
#     return render(request, 'vendor/add_products.html', {'form': form})

@login_required(login_url='vendor:actor_authentication:login_all')
@vendor_required
def add_products_all(request):
    return render(request, 'vendor/add_products_all.html')


def add_product_existing(request):
    categories = Category.objects.all()
    return render(request, 'vendor/index.html', context={'categories': categories})


def add_existing_prod(request, cat_id, p_id):
    form = AddExisting()
    if request.method == 'POST':
        form = AddExisting(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['qty']
            p = Product.objects.get(pk=p_id)
            v = VendorQty.objects.get(Vendor=request.user, product=p)
            # v.product = p
            v.qty = quantity
            v.save()
            return redirect('vendor:view_products')

    return render(request, 'vendor/add_existing_product.html', context={'form': form})


def add_product_new(request):
    form = AddNew()
    if request.method == 'POST':
        form = AddNew(request.POST)
        if form.is_valid():
            name = form.cleaned_data['prod_name']
            if Product.objects.filter(prod_name=name).exists():
                error_msg = 'Product already exists'
                return render(request, 'vendor/add_new_product.html', {'form': form, 'msg': error_msg})

            else:
                form.save()
                return redirect('vendor:view_products')
        else:
            print('The form is invalid')

    return render(request, 'vendor/add_new_product.html', {'form': form})


def itemsview(request, pk):
    categories = Category.objects.all()
    cat = Category.objects.get(id=pk)
    context = {
        'categories': categories,
        'cat': cat
    }

    return render(request, "vendor/items.html", context)


@login_required(login_url='vendor:actor_authentication:login_all')
@vendor_required
def view_products(request):
    product_list = Product.objects.all().order_by('prod_name')
    current_order_products = []
    query = request.GET.get('q')
    if query:
        product_list = Product.objects.filter(
            Q(prod_name__icontains=query) |
            Q(brand__icontains=query) |
            Q(category__cat_name__contains=query)
        )
    paginator = Paginator(product_list, 10)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    return render(request, 'vendor/view_products.html', {'products': products})


@login_required(login_url='vendor:actor_authentication:login_all')
@vendor_required
def modify_products(request, id):
    product = Product.objects.get(pk=id)
    vendor_qty = VendorQty.objects.get(Vendor=request.user, product=product)
    product_form = ProductsAdd(instance=product)
    vendor_form = VendorForm(instance=vendor_qty)
    if request.method == 'POST':
        product_form = ProductsAdd(request.POST, instance=product)
        vendor_form = VendorForm(request.POST, instance=vendor_qty)
        if product_form.is_valid() and vendor_form.is_valid():
            product_form.save()
            vendor_form.save()
            return redirect('vendor:view_products')
        else:
            print('Forms are invalid')
    return render(request, 'vendor/modify_product.html', {'product_form': product_form, 'vendor_form': vendor_form})


@login_required(login_url='vendor:actor_authentication:login_all')
@vendor_required
def delete_product(request, id):
    product = Product.objects.get(pk=id)
    name = product.prod_name
    product.delete()
    return redirect('vendor:view_products')


@login_required(login_url='vendor:actor_authentication:login_all')
@vendor_required
def view_orders(request):
    orders = Order.objects.filter(is_ordered=True, vendor=request.user)
    return render(request, 'vendor/show_orders.html', {'orders': orders})


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
