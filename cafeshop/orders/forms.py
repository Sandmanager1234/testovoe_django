from django.forms import ModelForm, ModelChoiceField, IntegerField, Form, NumberInput

from .models import Order, OrderItemRelation
from items.models import Item


# Форма для добавления товаров в заказ
class OrderItemForm(Form):
    item = ModelChoiceField(queryset=Item.objects.all(), required=True)
    count = IntegerField(min_value=1, max_value=255, required=True)


# форма заказа
class OrderModelForm(Form):
    table_number = IntegerField(max_value=100, min_value=1, required=True)


# форма смены статуса
class OrderUpdateForm(ModelForm):
    class Meta:
        model = Order
        fields = ['status']



# class OrderItemForm(ModelForm):
#     class Meta:
#         model = OrderItemRelation
#         fields = ['item', 'count']
# 
#     widgets = {
#         'item': ModelChoiceField(
#             queryset=Item.objects.all(), required=True
#         ),
#         'count': IntegerField(
#             attrs={
#                 'class': 'form-control',
#                 'min': "1"
#             }
#         )
#     }
    

# class OrderModelForm(ModelForm):
#     class Meta:
#         model = Order
#         fields = ['table_number']
# 
#     widgets = {
#         'table_number': NumberInput(
#             attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Номер столика',
#                 'min': 1
#             }
#         )
#     }
    
    
