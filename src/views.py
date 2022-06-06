import random
import string
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import CheckoutForm, CouponForm, RefundForm, PaymentForm
from .models import Item, OrderItem, Order, Address, Payment, Coupon, Refund, CATEGORY_CHOICES


def create_ref_code():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=20))


class Home(ListView):
    model = Item
    paginate_by = 4
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        context["categories"] = dict(CATEGORY_CHOICES)
        return context


def get_all_products(request):
    context = {"items": Item.objects.all(), "categories": dict(CATEGORY_CHOICES)}
    return render(request, "products.html", context)


def get_products_by_category(request, category):
    context = {"items": Item.objects.filter(category=category), "categories": dict(CATEGORY_CHOICES)}
    return render(request, "products.html", context)


def products_with_discount(request):
    context = {"items": Item.objects.filter(discount_price__isnull=False), "categories": dict(CATEGORY_CHOICES)}
    return render(request, "products.html", context)



@login_required
def cart(request):
    try:
        order = Order.objects.filter(user=request.user, ordered=False).first()
        context = {"order": order}
        return render(request, "cart.html", context)
    except ObjectDoesNotExist:
        messages.warning(request, "You don't have an active order")
        return redirect("/")


def is_valid_form(values):
    valid = True
    for field in values:
        if field == "":
            valid = False
    return valid


class Checkout(View, LoginRequiredMixin):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {"form": form, "order": order, "couponForm": CouponForm(), "DISPLAY_COUPON_FORM": True}
            shipping_address_qs = Address.objects.filter(user=self.request.user, address_type='S', default=True)
            if shipping_address_qs.exists():
                context.update({"default_shipping_address": shipping_address_qs[0]})
            billing_address_qs = Address.objects.filter(user=self.request.user, address_type='B', default=True)
            if billing_address_qs.exists():
                context.update({"default_billing_address": billing_address_qs[0]})
            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You don't have an active order!")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.filter(user=self.request.user, ordered=False).first()
            if form.is_valid():
                use_default_shipping = form.cleaned_data.get("use_default_shipping")
                if use_default_shipping:
                    address_qs = Address.objects.filter(user=self.request.user, address_type='S', default=True)
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(self.request, "No default shipping address available")
                        return redirect("core:checkout")
                else:
                    shipping_address1 = form.cleaned_data.get("shipping_address")
                    shipping_address2 = form.cleaned_data.get("shipping_address2")
                    shipping_country = form.cleaned_data.get("shipping_country")
                    shipping_zip = form.cleaned_data.get("shipping_zip")
                    if is_valid_form([shipping_address1, shipping_country, shipping_zip]):
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            zip=shipping_zip,
                            address_type='S'
                        )
                        shipping_address.save()
                        order.shipping_address = shipping_address
                        order.save()
                        set_default_shipping = form.cleaned_data.get("set_default_shipping")
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()
                    else:
                        messages.info(self.request, "Please fill in the required shipping address fields")

                use_default_billing = form.cleaned_data.get("use_default_billing")
                same_billing_address = form.cleaned_data.get("same_billing_address")
                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()
                elif use_default_billing:
                    address_qs = Address.objects.filter(user=self.request.user, address_type='B', default=True)
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(self.request, "No default billing address available")
                        return redirect("core:checkout")
                else:
                    billing_address1 = form.cleaned_data.get("billing_address")
                    billing_address2 = form.cleaned_data.get("billing_address2")
                    billing_country = form.cleaned_data.get("billing_country")
                    billing_zip = form.cleaned_data.get("billing_zip")
                    if is_valid_form([billing_address1, billing_country, billing_zip]):
                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            country=billing_country,
                            zip=billing_zip,
                            address_type='B'
                        )
                        billing_address.save()
                        order.billing_address = billing_address
                        order.save()
                        set_default_billing = form.cleaned_data.get("set_default_billing")
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()
                    else:
                        messages.info(self.request, "Please fill in the required billing address fields")
                payment_option = form.cleaned_data.get("payment_option")
                if payment_option == 'S':
                    return redirect("core:payment", payment_option="stripe")
                elif payment_option == 'P':
                    return redirect("core:payment", payment_option="paypal")
                else:
                    messages.warning(self.request, "Invalid payment option selected")
                    return redirect("core:checkout")
            else:
                messages.warning(self.request, "Failed checkout")
                return redirect("core:checkout")
        except ObjectDoesNotExist:
            messages.warning(self.request, "You don't have an active order")
            return redirect("core:cart")


class PaymentView(View, LoginRequiredMixin):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {"order": order, "DISPLAY_COUPON_FORM": False}
            return render(self.request, "payment.html", context)
        else:
            messages.warning(self.request, "You have not added a billing address")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        # create the payment
        payment = Payment.objects.create(user=self.request.user, amount=order.get_total_price())
        # assign the payment to the order
        order_items = order.items.all()
        order_items.update(ordered=True)
        for item in order_items:
            item.save()
        order.ordered = True
        order.payment = payment
        order.ref_code = create_ref_code()
        order.save()
        messages.success(self.request, "Your order was successful!")
        return redirect("/")


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(item=item, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart")
    return redirect("core:cart")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            order_item.quantity -= 1
            order_item.save()
            if order_item.quantity == 0:
                order_item.delete()
            messages.info(request, "This item quantity was updated")
            return redirect("core:cart")
        else:
            messages.info(request, "This item was not in your cart")
    else:
        messages.info(request, "You don't have an active order")
    return redirect("core:product", slug=slug)


@login_required
def remove_completely_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            order_item.delete()
            messages.info(request, "This item was removed from your cart")
            return redirect("core:cart")
        else:
            messages.info(request, "This item was not in your cart")
    else:
        messages.info(request, "You don't have an active order")
    return redirect("core:product", slug=slug)


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("core:checkout")


class AddCoupon(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get("code")
                order = Order.objects.get(user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.info(self.request, "Successfully added coupon")
                return redirect("core:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You don't have an active order!")
                return redirect("core:checkout")
        else:
            messages.warning(self.request, "Failed coupon")
            return redirect("core:add_coupon")


class RequestRefund(View, LoginRequiredMixin):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {"form": form, "ref_code": self.kwargs["ref_code"]}
        return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST or None)
        if form.is_valid():
            ref_code = form.cleaned_data.get("ref_code")
            message = form.cleaned_data.get("message")
            email = form.cleaned_data.get("email")
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_request = True
                order.save()
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()
                messages.info(self.request, "Your request was received")
                return redirect("/")
            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist")
                return redirect("core:request_refund", ref_code=ref_code)
        else:
            messages.warning(self.request, "Failed request")
            return redirect("core:request_refund", ref_code=self.kwargs["ref_code"])

@login_required
def my_orders(request):
    required_date = datetime.now() - timedelta(days=7)
    orders = Order.objects.filter(user=request.user, ordered=True, refund_granted=False, ordered_date__gt=required_date)
    context = {"orders": orders}
    return render(request, "my_orders.html", context)






