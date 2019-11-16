from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from cart.models import OrderItem, Order, Transaction
from customer.forms import Contact_Form
from vendor.models import Product, VendorQty
from customer.models import CustomerProfile
from cart.extra import generate_order_id
import datetime
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string


def get_user_pending_order(request):
    user_profile = get_object_or_404(CustomerProfile, Customer=request.user)
    ord = Order.objects.filter(owner=user_profile, is_ordered=False)
    if ord.exists():
        return ord[0]
    return 0


@login_required(login_url='customer:actor_authentication:login_all')
def add_to_cart(request, prod_id):
    if request.GET:
        vendorid = request.GET['vendorid']
        # print(vendorid)
        ven_qty = VendorQty.objects.get(id=vendorid)
        ven = ven_qty.Vendor
        # print(ven)
        # print(ven_qty)

    user_profile = get_object_or_404(CustomerProfile, Customer=request.user)
    product = Product.objects.get(id=prod_id)

    user_order, status = Order.objects.get_or_create(owner=user_profile, is_ordered=False)

    if status:
        ref_code = generate_order_id()
        # print(ref_code)
        order_item, status = OrderItem.objects.get_or_create(product=product, ref_code=ref_code)
        order_item.vendor.add(ven)
        user_order.items.add(order_item)
        user_order.vendor.add(ven)
        user_order.ref_code = ref_code
        user_order.save()
    else:
        order_item, status = OrderItem.objects.get_or_create(product=product, ref_code=user_order.ref_code)
        order_item.vendor.add(ven)
        user_order.items.add(order_item)
        user_order.vendor.add(ven)
        user_order.save()

    if request.GET:
        nextto = request.GET["nextto"]
        return redirect(nextto)
    else:
        return HttpResponse('')


@login_required(login_url='customer:actor_authentication:login_all')
def delete_from_cart(request, item_id):
    item_to_delete = OrderItem.objects.filter(pk=item_id)
    if item_to_delete.exists():
        item_to_delete[0].delete()
    return redirect(reverse('cart:order_summary'))


@login_required(login_url='customer:actor_authentication:login_all')
def order_details(request, **kwargs):
    existing_order = get_user_pending_order(request)

    context = {
        'order': existing_order
    }
    return render(request, 'cart/order_summary.html', context)


@login_required(login_url='customer:actor_authentication:login_all')
def checkout(request, **kwargs):
    existing_order = get_user_pending_order(request)
    context = {
        'ordre': existing_order
    }

    return render(request, 'cart/checkout.html', context)


def get_user_details(request):
    u = CustomerProfile.objects.get(Customer=request.user)
    user_form = Contact_Form(instance=u)

    if request.method == 'POST':
        user_form = Contact_Form(request.POST, instance=u)
        if user_form.is_valid():

            order_to_purchase = get_user_pending_order(request)

            order_to_purchase.is_ordered = True
            order_to_purchase.date_ordered = datetime.datetime.now()

            customer = order_to_purchase.owner.Customer.username

            order_to_purchase.save()

            order_items = order_to_purchase.items.all()

            sportshub_order_items = []
            flag = 0
            for item in order_items:
                ven = item.vendor.all()[0]
                print('The vendor is', ven)
                if str(ven) == 'sportshub':
                    flag = 1
                    print(ven)
                    sportshub_order_items.append({item.product.prod_name: item.qty})
                    print(sportshub_order_items)
                ven_qty = VendorQty.objects.get(Vendor=ven, product=item.product)

                # print(ven_qty.qty)
                ven_qty.qty -= item.qty

                # print(ven_qty.qty)
                ven_qty.save()

            if len(sportshub_order_items) > 0:
                print('An order has been placed')
                current_site = get_current_site(request)
                mail_subject = 'SportsHub Order Placed'
                message = render_to_string('cart/send_email.html', {
                    'domain': current_site.domain,
                    'user': customer,
                    'items': sportshub_order_items
                })
                email = EmailMessage(
                    mail_subject, message, to=[User.objects.get(username='sportshub').email]
                )
                email.send()

            order_items.update(is_ordered=True, date_ordered=datetime.datetime.now())

            transaction = Transaction(profile=request.user.cus,
                                      order_id=order_to_purchase.ref_code,
                                      amount=order_to_purchase.get_cart_total(),
                                      success=True)

            transaction.save()

            address = user_form.cleaned_data['address']
            phone_num = user_form.cleaned_data['phone_number']
            user_form.save()

            subject = 'Your order has been successfully placed'
            context = {
                'ordre': order_to_purchase,
                'user': request.user,
                'total': order_to_purchase.get_cart_total(),
                'address': address,
                'contact_details': phone_num,
                'ref_code': order_to_purchase.ref_code
            }
            html = render_to_string('cart/message.html', context)
            message = render_to_string('cart/message.html', context)
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [request.user.email]

            send_mail(subject, message, email_from, recipient_list, fail_silently=False, html_message=html)
            messages.info(request, "Thank you! Your purchase was successful!")

            return render(request, 'cart/show_final_details.html', {'address': address,
                                                                    'phone_number': phone_num,
                                                                    'ref_code': order_to_purchase.ref_code})

    return render(request, 'cart/get_user_details.html', {'form': user_form})


@login_required(login_url='customer:actor_authentication:login_all')
def update_transaction_records(request):
    return redirect('cart:get_user_details')


def qtyupdate(request):
    a = request.POST.get('item_id')
    if request.method == "POST":
        order_id = request.POST["order_id"]
        item_id = request.POST["item_id"]
        qty = request.POST["z"]
        order = get_user_pending_order(request)
        item = order.items.get(pk=item_id)
        item.qty = qty
        # print("data: " + item_id + "        " + order_id + "           " + qty)
        item.save()
        order.save()
    return HttpResponse(" ")
