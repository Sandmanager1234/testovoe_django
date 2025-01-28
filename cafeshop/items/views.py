from django.views.generic import ListView

from .models import Item

# Вьюшка отображения списка товаров (нет никакого функционала)
class ItemsListView(ListView):
    template_name = 'templates/items/items.html'
    model = Item
    context_object_name = 'items'

    def get_queryset(self):
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Товары'
        return context
