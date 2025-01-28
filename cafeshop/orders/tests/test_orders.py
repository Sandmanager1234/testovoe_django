from django.test import TestCase
from django.urls import reverse
from django.db.models import Sum, F
from orders.models import Order, OrderItemRelation, Item

'''
ORDERS:
1. ОТОБРАЖЕНИЕ СПИСКА ВСЕХ ЗАКАЗОВ .... Ready
2. ПОИСК ЗАКАЗОВ ...................... Ready
3. СОЗДАНИЕ ЗАКАЗА .................... Ready
4. УДАЛЕНИЕ ЗАКАЗА .................... Ready
5. РЕДАКТИРОВНАИЕ ЗАКАЗА .............. Ready
6. Получение выручки ..................
'''
# Create your tests here.
class GetOrdersTestCase(TestCase):

    def setUp(self):
        self.item1 = Item.objects.create(title='Кофе', price=150)
        self.item2 = Item.objects.create(title='Торт', price=250)
        self.order1 = Order.objects.create(table_number=1)
        self.order2 = Order.objects.create(table_number=2, status='Готово')
        self.orderitem1 = OrderItemRelation.objects.create(order=self.order1, item=self.item1, count=1)
        self.orderitem2 = OrderItemRelation.objects.create(order=self.order1, item=self.item2, count=2)
        self.orderitem3 = OrderItemRelation.objects.create(order=self.order2, item=self.item1, count=2)
        return super().setUp()
    
    def test_get_order_list(self):
        url = reverse('orders:order-api-list')
        resp_json = self.client.get(url).json()
        orders = Order.objects.all().prefetch_related(
            'orders'
        ).prefetch_related(
            'orders__item'
        ).annotate(
            total_price=Sum(F('orders__item__price') * F('orders__count'))
        ).order_by(
            '-created_at'
        )
        data_json = [
        {
            'id': order.id,
            'status': order.status,
            'table_number': order.table_number,
            'items': [
                {
                    'id': rel.item.id,
                    'title': rel.item.title,
                    'price': '{:.2f}'.format(rel.item.price),
                    'count': rel.count
                } for rel in order.orders.all()
            ],
            'total_price': '{:.2f}'.format(order.total_price)
        } for order in orders
    ]
        self.assertEqual(first=data_json, second=resp_json, msg=f'Не совпадает')

    def test_get_search_by_table_number_order_list(self):
        url = reverse('orders:order-api-list')
        resp_json = self.client.get(url, data={'q': '1'}).json()
        data_json = [
            {
                'id': self.order1.id,
                'status': self.order1.status.value,
                'table_number': self.order1.table_number,
                'items': [
                    {
                        'id': rel.item.id,
                        'title': rel.item.title,
                        'price': '{:.2f}'.format(rel.item.price),
                        'count': rel.count
                    } for rel in self.order1.orders.all()
                ],
                'total_price': '{:.2f}'.format(self.orderitem1.item.price * self.orderitem1.count 
                                               + self.orderitem2.item.price * self.orderitem2.count)
            } 
        ]
        self.assertEqual(first=data_json, second=resp_json, msg=f'Не совпадает')

    def test_get_search_by_status_order_list(self):
        url = reverse('orders:order-api-list')
        resp = self.client.get(url, data={'q': 'Готово'})
        data_json = [
            {
                'id': self.order2.id,
                'status': self.order2.status,
                'table_number': self.order2.table_number,
                'items': [
                    {
                        'id': rel.item.id,
                        'title': rel.item.title,
                        'price': '{:.2f}'.format(rel.item.price),
                        'count': rel.count
                    } for rel in self.order2.orders.all()
                ],
                'total_price': '{:.2f}'.format(self.orderitem3.item.price * self.orderitem3.count)
            } 
        ]
        self.assertEqual(resp.status_code, 200, 'Неверный статус')
        self.assertEqual(first=data_json, second=resp.json(), msg=f'Не совпадает')

    def test_get_search_by_both_fields_order_list(self):
        url = reverse('orders:order-api-list')
        resp = self.client.get(url, data={'q': 'Готово 2'})
        data_json = [
            {
                'id': self.order2.id,
                'status': self.order2.status,
                'table_number': self.order2.table_number,
                'items': [
                    {
                        'id': rel.item.id,
                        'title': rel.item.title,
                        'price': '{:.2f}'.format(rel.item.price),
                        'count': rel.count
                    } for rel in self.order2.orders.all()
                ],
                'total_price': '{:.2f}'.format(self.orderitem3.item.price * self.orderitem3.count)
            } 
        ]
        self.assertEqual(resp.status_code, 200, 'Неверный статус')
        self.assertEqual(first=data_json, second=resp.json(), msg=f'Не совпадает')

    def test_success_create_order(self):
        url = reverse('orders:order-api-list')
        old_len = len(Order.objects.all())
        body = {
            'table_number': 3,
            'items': [
                {
                    'id': self.item1.id,
                    'count': 3
                }
            ]
        }
        resp_json = self.client.post(url, data=body, content_type='application/json')
        self.assertEqual(resp_json.status_code, 201, resp_json.json())
        self.assertEqual(len(Order.objects.all()), old_len + 1, 'Нет нового объекта')

    def test_failed_create_order(self):
        url = reverse('orders:order-api-list')
        old_len = len(Order.objects.all())
        body = {
            'table_number': 3,
            'items': [
                {
                    'id': self.item1.id,
                    'count': -1
                }
            ]
        }
        resp_json = self.client.post(url, data=body, content_type='application/json')
        self.assertEqual(resp_json.status_code, 400, 'Неверный статус')
        self.assertEqual(len(Order.objects.all()), old_len, 'Новый объект есть')

    def test_success_update_order(self):
        url = reverse('orders:order-api-ud', args=(self.order2.id, ))
        new_status = "Оплачено"
        data = {
            "status": new_status
        }
        resp = self.client.put(url, data=data, content_type='application/json')
        self.order2.refresh_from_db()
        self.assertEqual(resp.status_code, 200, 'Неверный статус')
        self.assertEqual(self.order2.status, new_status)

    def test_failed_update_order(self):
        url = reverse('orders:order-api-ud', args=(self.order1.id, ))
        old_status = self.order1.status
        new_status = "прикол"
        data = {
            "status": new_status
        }
        resp = self.client.put(url, data=data, content_type='application/json')
        self.order1.refresh_from_db()
        self.assertEqual(resp.status_code, 400, 'Неверный статус')
        self.assertEqual(self.order1.status, old_status)

    def test_success_delete_order(self):
        order_id = self.order1.id
        url = reverse('orders:order-api-ud', args=(order_id, ))
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 204, 'Неверный статус')
        self.assertEqual(len(Order.objects.filter(id=order_id)), 0)

    def test_failed_delete_order(self):
        order_id = 0
        url = reverse('orders:order-api-ud', args=(order_id, ))
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 400, 'Неверный статус')

    def test_get_revenue(self):
        url = reverse('orders:order-api-revenue')
        resp = self.client.get(url)
        qs = Order.objects.prefetch_related(
                'orders'
            ).prefetch_related(
                'orders__item'
            ).annotate(
                total_price=Sum(F('orders__item__price') * F('orders__count'))
            ).order_by(
                '-created_at'
            ).filter(status='Готово')
        data = {
            'orders': [
                {
                    'id': order.id,
                    'status': order.status,
                    'table_number': order.table_number,
                    'items': [
                        {
                            'id': rel.item.id,
                            'title': rel.item.title,
                            'price': '{:.2f}'.format(rel.item.price),
                            'count': rel.count
                        } for rel in order.orders.all()
                    ],
                    'total_price': '{:.2f}'.format(order.total_price)
                }  for order in qs
            ],
            'total': '{:.2f}'.format(qs.aggregate(total=Sum('total_price')).get('total'))
        }
        self.assertEqual(resp.status_code, 200, 'Неверный статус')
        self.assertEqual(resp.json(), data, resp.json())