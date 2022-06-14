from django.db import models
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
            summ_price += item.price
            self.date = max(self.date, item.date)
        self.price = summ_price
        self.amount = amount
        self.save()
        if self.parentId is not None:
            self.parentId.check_children()


    def get_price(self):
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


class PriceChange(models.Model):
    unit = models.ForeignKey(to=ShoppingUnit, on_delete=models.CASCADE)
    date = models.DateTimeField()
    price = models.IntegerField()


    def getType(self):
        return self.unit.type







