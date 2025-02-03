from django.urls import path, include

from . import views
from . import api_views

app_name = 'orders'

api_urls = [
    path('api/v1/orders', api_views.orders_list_rest_api, name='order-api-list'),
    path('api/v1/orders/revenue', api_views.get_revenue, name='order-api-revenue'),
    path('api/v1/orders/<int:pk>', api_views.order_update_delete_api, name='order-api-ud'),
]

urlpatterns = [
    path('', views.OrderListView.as_view(), name='order-list'),
    path('paid', views.OrderPaidView.as_view(), name='order-paid'),
    path('<int:pk>/edit', views.OrderUpdateView.as_view(), name='order-edit'),
    path('create', views.create_order, name='order-create'),
    path('<int:pk>/delete', views.OrderDeleteView.as_view(), name='order-delete'),

    # API
    path('api/', include(api_urls))
]

