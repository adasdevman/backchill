from django import template

register = template.Library()

@register.filter
def get_color(index):
    colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']
    return colors[index % len(colors)]

@register.filter
def index(lst, i):
    try:
        return lst[i]
    except:
        return None 