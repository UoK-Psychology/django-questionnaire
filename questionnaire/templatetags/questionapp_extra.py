'''
 store custom template tags 
'''
from django import template
register = template.Library()

@register.filter('klass')
def klass(obj):
    return obj.__class__.__name__