from django.db import models
from django.conf import settings
from datetime import timezone
import datetime
from django.urls import reverse
from django_countries.fields import CountryField

CATEGORY_CHOICES = (
    ('C', "Clothes"),
    ("P", "PC"),
    ("PH", "Phones"),
    ("T", "TV"),
    ("CO", "Console")
)

ADDRESS_CHOICES = (
    ('S', "Shipping"),
    ('B', "Billing")
)


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    description = models.TextField()
    is_new = models.BooleanField(default=True)
    slug = models.SlugField()
    image = models.ImageField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # kwargs used to pass the argument to the url
        return reverse("core:product", kwargs={"slug": self.slug})

    def get_add_to_cart_url(self):
        return reverse("core:add_to_cart", kwargs={"slug": self.slug})

    def get_remove_from_cart_url(self):
        return reverse("core:remove_completely_from_cart", kwargs={"slug": self.slug})

    def is_new_verif(self):
        if datetime.datetime.now(timezone.utc) - self.created_at > datetime.timedelta(days=5):
            return False
        else:
            return True


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        if self.item.discount_price:
            return self.quantity * self.item.discount_price
        else:
            return self.quantity * self.item.price


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey("Address", related_name="billing_address", on_delete=models.SET_NULL, blank=True, null=True)
    shipping_address = models.ForeignKey("Address", related_name="shipping_address", on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey("Payment", on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey("Coupon", on_delete=models.SET_NULL, blank=True, null=True)
    delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_request = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def get_total_price(self):
        somme = 0
        for item in self.items.all():
            somme += item.get_total_item_price()
        if self.coupon:
            somme -= self.coupon.amount
        return somme


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.street_address

    class Meta:
        verbose_name_plural = "Addresses"


class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"${self.amount} from {self.user}"


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


