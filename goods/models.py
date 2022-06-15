from django.db import models
from django.shortcuts import get_object_or_404
from goods.date_validator import DateValidator



class ShoppingUnit(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=1000)
    date = models.DateTimeField()
    parentId = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    price = models.IntegerField(default=0, null=True)
    amount = models.IntegerField(default=1)
    type = models.CharField(max_length=100, choices=(("OFFER", "OFFER"), ("CATEGORY", "CATEGORY")))

    def check_children(self):

        children = ShoppingUnit.objects.filter(parentId = self)
        summ_price = 0
        amount = 0
        price_change = PriceChange(unit=self, date=self.date, price=self.get_price())
        price_change.save()
        for item in children:
            amount += item.amount
            if item.price is not None:
                summ_price += item.price
            self.date = max(self.date, item.date)
        self.price = summ_price
        self.amount = amount
        self.save()
        print(self.name, self.amount, self.price)

        if self.parentId is not None:
            self.parentId.check_children()


    def get_price(self):
        if self.price is None:
            return None
        if self.amount != 0:
            return self.price // self.amount
        else:
            return 0


    def json_build(self):
        json_dict = dict()
        json_dict['id'] = self.id
        json_dict['name'] = self.name
        json_dict['date'] = DateValidator.dateToString(self.date)

        json_dict['type'] = self.type
        json_dict['price'] = self.get_price()
        if json_dict['price'] == 0 and self.type == "CATEGORY":
            json_dict['price'] = None
        if self.parentId is not None:
            json_dict['parentId'] = self.parentId.id
        else:
            json_dict['parentId'] = None
        children = ShoppingUnit.objects.filter(parentId = self)
        if len(children) > 0:
            json_dict['children'] = []
            for item in children:
                json_dict['children'].append(item.json_build())
        else:
            json_dict['children'] = None
        return json_dict
        

    def custom_delete(self):
        parent = self.parentId
        self.delete()
        if parent is not None:
            parent.check_children()

    @staticmethod
    def save_import(item, date):
        print("saving", item['name'])
        try:
            unit = ShoppingUnit.objects.get(pk=item['id'])
            price_change = PriceChange(unit=unit, date=unit.date, price=unit.get_price())
            price_change.save()
        except ShoppingUnit.DoesNotExist:
            unit = ShoppingUnit()
            unit.id = item['id']
            unit.type = item['type']

        unit.name = item['name']
        unit.date = date
        unit.price = item.get('price')
        if unit.type == "CATEGORY":
            unit.amount = 0
        else:
            unit.amount = 1
        if item.get('parentId') is not None:
            unit.parentId = get_object_or_404(ShoppingUnit, pk=item['parentId'])
            unit.save()
            unit.parentId.check_children()
        unit.save()


class PriceChange(models.Model):
    unit = models.ForeignKey(to=ShoppingUnit, on_delete=models.CASCADE)
    date = models.DateTimeField()
    price = models.IntegerField(null=True, blank=True)


    def getType(self):
        return self.unit.type







