from django import template

register = template.Library()


@register.filter
def get_item_name(prod):
    for name, qty in prod.items():
        return name


@register.filter
def get_item_qty(prod):
    for name, qty in prod.items():
        return qty
