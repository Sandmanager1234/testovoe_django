from django.db import models
from django.urls import reverse_lazy

from items.models import Item


# Модель заказа
class Order(models.Model):
    class StatusType(models.TextChoices):
        PENDING = 'В ожидании'
        READY = 'Готово'
        PAID = 'Оплачено'
    
    table_number = models.IntegerField()
    status = models.CharField(choices=StatusType, default=StatusType.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse_lazy('orders:order-list')

    def __str__(self):
        return f'ID: {self.id}; Стол: {self.table_number}; Статус: {self.status}'


# Модель связи заказа и товара
class OrderItemRelation(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='items')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='orders')
    count = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'item: {self.item_id}; order:{self.order_id}'