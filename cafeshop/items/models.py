from django.db import models


class Item(models.Model):
    title = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f'{self.title} price: {self.price}'
