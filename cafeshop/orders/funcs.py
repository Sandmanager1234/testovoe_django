from django.db.models import Sum, F, QuerySet

from items.models import Item
from orders.models import Order


# Создание queryset для дальнейшей обработки
def get_api_queryset():
    '''Функция получения Queryset`a с аннотацией'''
    orders = Order.objects.all().prefetch_related(
            'orders'
        ).prefetch_related(
            'orders__item'
        ).annotate(
            total_price=Sum(F('orders__item__price') * F('orders__count'))
        ).order_by(
            '-created_at'
        )
    return orders


# Получение JSON из queryset
def get_orders_json(orders: QuerySet):
    '''Функция получения JSON объекта со списком заказов'''
    data = [
        {
            'id': order.id,
            'status': order.status,
            'table_number': order.table_number,
            'items': [
                {
                    'id': rel.item.id,
                    'title': rel.item.title,
                    'price': rel.item.price,
                    'count': rel.count
                } for rel in order.orders.all()
            ],
            'total_price': order.total_price
        } for order in orders
    ]
    return data


def find_items_in_order(items: list[dict]):
    '''Функция нахождения товаров и общей суммы заказа'''
    items_obj = []
    total_price = 0
    for item in items:
        item_id = item.get('id')
        item_count = int(item.get('count'))
        if item_id and item_count and item_count > 0:
            item = Item.objects.get(id=item_id)
            items_obj.append([item, item_count])
            total_price += item_count * item.price
        else:
            raise Exception(f'Некорректные данные item. id: {item_id}, count: {item_count};')
        
    return items_obj, total_price