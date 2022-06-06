from django import template
from src.models import Order

register = template.Library()


@register.filter
def cart_items_count(user):
    if user.is_authenticated:
        qs = Order.objects.filter(user=user, ordered=False).first()
        somme = 0
        if qs:
            items = qs.items.all()
            for item in items:
                somme += item.quantity
        return somme
