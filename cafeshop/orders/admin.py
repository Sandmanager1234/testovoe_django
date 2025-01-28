from django.contrib import admin

from .models import Order, OrderItemRelation


# Register your models here.
# Зарегистрировал объекты в админке
admin.site.register(Order)
admin.site.register(OrderItemRelation)
