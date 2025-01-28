from django.urls import path

from . import views

app_name = 'items'

urlpatterns = [
    path('', views.ItemsListView.as_view(), name='item-list'),
]
