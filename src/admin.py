from django.contrib import admin
from .models import Item, OrderItem, Order, Payment, Coupon, Refund, Address


def refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_request=False, refund_granted=True)


def order_delivered(modeladmin, request, queryset):
    queryset.update(delivered=True)


def order_received(modeladmin, request, queryset):
    queryset.update(received=True)


refund_accepted.short_description = "Update orders to refund granted"
order_delivered.short_description = "Update orders to delivered"
order_received.short_description = "Update orders to received"


class OrderAdmin(admin.ModelAdmin):
    list_display = ["user", "ordered", "delivered", "received", "refund_request", "refund_granted", "billing_address", "shipping_address", "payment", "coupon"]
    list_display_links = ["user", "billing_address", "shipping_address", "payment", "coupon"]
    list_filter = ["user", "ordered", "delivered", "received", "refund_request", "refund_granted"]
    search_fields = ["user__username", "ref_code"]
    actions = [refund_accepted, order_delivered, order_received]


class AddressAdmin(admin.ModelAdmin):
    list_display = ["user", "street_address", "apartment_address", "country", "zip", "address_type", "default"]
    list_filter = ["default", "address_type", "country"]
    search_fields = ["user__username", "street_address", "apartment_address", "zip"]


# Register your models here.
admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(Address, AddressAdmin)

