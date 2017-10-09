import json

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def string_value(value, markers):
    value = escape(value)
    if markers:
        markers = json.loads(markers)
        for marker, marker_details in markers.items():
            marker = escape(marker)
            marker_name = marker_details['name'] or ''
            value = value.replace(marker, '<span class="text-danger" title="{1}">{0}</span>'.format(marker, marker_name))
    return mark_safe(value)
