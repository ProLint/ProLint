import os
from django import template

register = template.Library()

@register.filter
def filename(value):
    return value.url.split('/')[-1]

