from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='order-list'),
    path('paid', views.OrderPaidView.as_view(), name='order-paid'),
    path('<int:pk>/edit', views.OrderUpdateView.as_view(), name='order-edit'),
    path('create', views.create_order, name='order-create'),
    path('<int:pk>/delete', views.OrderDeleteView.as_view(), name='order-delete'),

    # API
    path('api/v1/orders', views.orders_list_rest_api, name='order-api-list'),
    path('api/v1/orders/revenue', views.get_revenue, name='order-api-revenue'),
    path('api/v1/orders/<int:pk>', views.order_update_delete_api, name='order-api-ud'),
]
