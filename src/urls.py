from django.urls import path
from .views import Home, Checkout, ItemDetailView, add_to_cart, remove_from_cart, cart, remove_completely_from_cart, PaymentView, AddCoupon, RequestRefund, get_all_products, get_products_by_category, products_with_discount, my_orders

app_name = "core"

urlpatterns = [
    path("", Home.as_view(), name="home"),
    path("cart", cart, name="cart"),
    path("checkout", Checkout.as_view(), name="checkout"),
    path("product/<slug>", ItemDetailView.as_view(), name="product"),
    path("add_to_cart/<slug>", add_to_cart, name="add_to_cart"),
    path("remove_from_cart/<slug>", remove_from_cart, name="remove_from_cart"),
    path("remove_completely_from_cart/<slug>", remove_completely_from_cart, name="remove_completely_from_cart"),
    path("payment/<payment_option>", PaymentView.as_view(), name="payment"),
    path("add_coupon", AddCoupon.as_view(), name="add_coupon"),
    path("request_refund/<ref_code>", RequestRefund.as_view(), name="request_refund"),
    path("products", get_all_products, name="get_all_products"),
    path("products/<category>", get_products_by_category, name="get_products_by_category"),
    path("discounts", products_with_discount, name="products_with_discount"),
    path("my_orders", my_orders, name="my_orders"),
]
