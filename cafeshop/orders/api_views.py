import json

from django.db.models import Sum
from django.http.request import HttpRequest
from django.http.response import JsonResponse
from django.contrib.postgres.search import SearchVector

from orders.models import Order, OrderItemRelation
from .funcs import get_api_queryset, get_orders_json, find_items_in_order


def create_order_api(request: HttpRequest) -> tuple[dict, int]:
    '''Функция создания заказа'''
    request_body = json.loads(request.body)
    items = request_body.get('items') 
    table_number = request_body.get('table_number')
    try:
        if table_number < 1:
            raise Exception('table_number не может быть меньше 1.')
        if len(items) == 0 or len(items) > 10:
            raise Exception('items не может быть пустым и иметь размер больше 10.')
        
        items_obj, total_price = find_items_in_order(items)
        order = Order.objects.create(table_number=table_number)
        order_items = []

        for item, item_count in items_obj:
            order_item = OrderItemRelation.objects.create(order=order, item=item, count=item_count)
            order_items.append(order_item)
            
        status = 201
        data = {
            'id': order.id,
            'status': order.status,
            'table_number': order.table_number,
            'items': [
                {
                    'id': rel.item.id,
                    'title': rel.item.title,
                    'price': rel.item.price
                } for rel in order_items
            ],
            'total_price': total_price
        }
    except Exception as e:
        data = {'error': str(e)}
        status = 400
    return data, status


def get_orders_api(request: HttpRequest) -> tuple[dict, int]:
    '''Функция получения списка заказов'''
    orders = get_api_queryset()
    search_query = request.GET.get('q')
    if search_query:
        orders = orders.annotate(
                        search=SearchVector("table_number", "status"),
                    ).filter(search=search_query)
    
    data = get_orders_json(orders)
    return data, 200


def delete_order_api(pk: int) -> tuple[dict, int]:
    '''Функция удаления заказа'''
    try:
        Order.objects.get(id=pk).delete()
        data = {'msg': 'Order was deleted'}
        status = 204
    except Exception as e:
        status = 400
        data = {'error': str(e)}
    return data, status


def update_order_api(request: HttpRequest, pk: int) -> tuple[dict, int]:
    '''Функция обновления статуса заказа'''
    body = json.loads(request.body)
    data = body.get('status')
    status_order = body.get('status')
    values = Order.StatusType.values
    try:
        if status_order not in values:
            raise Exception(f'Неизвестный статус. Выберите статус из списка: {values}')
        Order.objects.filter(id=pk).update(status=status_order)
        status = 200
        data = {'msg': 'field update success'}
    except Exception as e:
        status = 400
        data = {'error': str(e)}
    return data, status


# API получения списка заказов и создания нового
def orders_list_rest_api(request: HttpRequest) -> JsonResponse:
    '''View для обработки POST и GET запроса по одному адресу'''
    data = {}
    if request.method == 'POST':
        data, status = create_order_api(request)
    elif request.method == 'GET': # обработка GET запроса
        data, status = get_orders_api(request)
    else:
        status = 405
        data = {'msg': 'method not allowed'}
    return JsonResponse(data=data, status=status, safe=False)
    

# функция апдейта и удаления заказа
def order_update_delete_api(request: HttpRequest, pk: int) -> JsonResponse:
    '''View для обработки PUT и DELETE запроса по одному адресу'''
    if request.method == 'DELETE':
        data, status = delete_order_api(pk)
    elif request.method == 'PUT':
        data, status = update_order_api(request, pk)
    else:
        status = 405
        data = {'msg': 'method not allowed'}
    return JsonResponse(data=data, status=status, safe=False)


# получение выручки 
def get_revenue(request: HttpRequest) -> JsonResponse:
    '''Функция для получения информации о выручке и списком оплаченных заказов'''
    if request.method != 'GET':
        status = 405
        data = {'msg': 'method not allowed'}
        return JsonResponse(data=data, status=status, safe=False) 
    status=200
    orders = get_api_queryset().filter(status='Готово')
    orders_list = get_orders_json(orders)
    total = orders.aggregate(total=Sum('total_price')).get('total')
    data = {
        'total': total,
        'orders': orders_list 
    }
    return JsonResponse(data=data, status=status, safe=False)