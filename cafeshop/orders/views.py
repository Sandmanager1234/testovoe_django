import json

from django.db.models import Sum, F
from django.urls import reverse_lazy
from django.forms import formset_factory
from django.http.request import HttpRequest
from django.shortcuts import render, redirect
from django.http.response import JsonResponse
from django.contrib.postgres.search import SearchVector
from django.views.generic import DeleteView, ListView, UpdateView

from items.models import Item
from orders.models import Order, OrderItemRelation
from .forms import OrderModelForm, OrderItemForm, OrderUpdateForm


# вьюшка создания заказа
def create_order(request: HttpRequest):
    error = ''
    form = OrderModelForm
    formset = formset_factory(OrderItemForm, max_num=10, extra=1)
    
    if request.method == 'POST':
        f = form(request.POST)
        if f.is_valid():
            table_number = f.cleaned_data.get('table_number')
            fs = formset(request.POST)
            if fs.is_valid():
                order_items = fs.cleaned_data
                if len(order_items) == 1 and len(order_items[0]) == 0:
                    error = 'Нельзя создать пустой заказ'
                else:
                    order = Order.objects.create(table_number=table_number)
                    for elem in order_items:
                        item = elem.get('item')
                        count = elem.get('count')
                        if item and count:
                            OrderItemRelation.objects.create(order=order, item=item, count=count)
                    return redirect('orders:order-list')
            else:
                error = 'Неправильно заполнена форма состава заказа'
        else:
            error = 'Неверно заполнена форма заказа'

    context = {
        'form': form, 
        'formset': formset, 
        'error': error,
        'title': 'Оформить заказ'
    }

    return render(request, 'orders/order_create.html', context)

# вьюшка смены статуса заказа
class OrderUpdateView(UpdateView):
    model = Order
    form = OrderUpdateForm
    fields = ['status']
    template_name = 'orders/order_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Заказ №{self.object.id}'
        return context


# вьюшка удаления заказа
class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy('orders:order-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Удаление заказа №{self.object.id}'
        return context


# Представление для отображения списка заказов
class OrderListView(ListView):
    model = Order
    template_name = 'orders/orders.html'
    context_object_name = 'orders'
    
    # устанавливаем свой queryset
    def get_queryset(self):
      
        queryset = super().get_queryset().prefetch_related(
            'orders'
        ).prefetch_related(
            'orders__item'
        ).annotate(
            total_price=Sum(F('orders__item__price') * F('orders__count'))
        ).order_by(
            '-created_at'
        )

        # поиск по полям table_number и status
        if self.request.GET:
            search_query = self.request.GET.get('q')
            if search_query:
                queryset = queryset.annotate(
                                search=SearchVector("table_number", "status"),
                            ).filter(search=search_query)

        return queryset
    
    # добавляем в context название страницы
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Заказы'
        return context


#Вьюшка для отображения страницы выручки
class OrderPaidView(OrderListView):
    template_name = 'orders/orders_paid.html'

    def get_queryset(self): # Получение queryset
        queryset = super().get_queryset().filter(status='Оплачено')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Выручка'
        context['total'] = self.get_queryset().aggregate(total=Sum('total_price')).get('total')
        return context


# API без DRF, а так хотелось(((
# Создание queryset для дальнейшей обработки
def get_api_queryset():
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
def get_orders_json(orders):
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


# API получения списка заказов и создания нового
def orders_list_rest_api(request: HttpRequest):
    data = {}
    if request.method == 'POST':
        try:
            total_price = 0
            items_obj = []
            req_body = json.loads(request.body)
            table_number = req_body.get('table_number')
            if table_number < 1:
                raise Exception('table_number не может быть меньше 1.')
            items = req_body.get('items')
            if len(items) == 0 or len(items) > 10:
                raise Exception('items не может быть пустым и иметь размер больше 10.')
            for item in items:
                item_id = item.get('id')
                item_count = int(item.get('count'))
                if item_id and item_count and item_count > 0:
                    item = Item.objects.get(id=item_id)
                    items_obj.append([item, item_count])
                    total_price += item_count * item.price
                else:
                    raise Exception(f'Некорректные данные item. id: {item_id}, count: {item_count};')
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
        return JsonResponse(data=data, status=status, safe=False)
    # обработка GET запроса
    elif request.method == 'GET':
        orders = get_api_queryset()

        if request.GET:
            search_query = request.GET.get('q')
            if search_query:
                orders = orders.annotate(
                                search=SearchVector("table_number", "status"),
                            ).filter(search=search_query)
        
        data = get_orders_json(orders)
        return JsonResponse(data=data, safe=False)
    else:
        status = 405
        data = {'msg': 'method not allowed'}
        return JsonResponse(data=data, status=status, safe=False)
    

# функция апдейта и удаления заказа
def order_update_delete_api(request: HttpRequest, pk):
    if request.method == 'DELETE':
        try:
            Order.objects.get(id=pk).delete()
            data = {'msg': 'Order was deleted'}
            status = 204
        except Exception as e:
            status = 400
            data = {'error': str(e)}
        return JsonResponse(data, status=status, safe=False)
    elif request.method == 'PUT':
        try:
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)
            data = body.get('status')
            status_order = body.get('status')
            values = Order.StatusType.values
            if status_order not in values:
                raise Exception(f'Неизвестный статус. Выберите статус из списка: {values}')
            Order.objects.filter(id=pk).update(status=status_order)
            status = 200
            data = {'msg': 'field update success'}
        except Exception as e:
            status = 400
            data = {'error': str(e)}
        return JsonResponse(data, status=status, safe=False)
    else:
        status = 405
        data = {'msg': 'method not allowed'}
        return JsonResponse(data=data, status=status, safe=False)


# получение выручки 
def get_revenue(request: HttpRequest):
    if request.method == 'GET':
        status=200
        orders = get_api_queryset().filter(status='Готово')
        orders_list = get_orders_json(orders)
        total = orders.aggregate(total=Sum('total_price')).get('total')
        data = {
            'total': total,
            'orders': orders_list 
        }
    else:
        status = 405
        data = {'msg': 'method not allowed'}
    return JsonResponse(data=data, status=status, safe=False)