from django.db.models import Sum, F
from django.urls import reverse_lazy
from django.forms import formset_factory
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.postgres.search import SearchVector
from django.views.generic import DeleteView, ListView, UpdateView

from orders.models import Order, OrderItemRelation
from .forms import OrderModelForm, OrderItemForm, OrderUpdateForm


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


# вьюшка создания заказа
def create_order(request: HttpRequest) -> HttpResponse:
    '''VIEW создания заказа из формы на сайте'''
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