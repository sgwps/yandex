from django.db import models



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
        price_change = PriceChange(unit=self, date=self.date, price=self.get_price)
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
        return self.price // self.amount
        

class PriceChange(models.Model):
    unit = models.ForeignKey(to=ShoppingUnit, on_delete=models.CASCADE)
    date = models.DateTimeField()
    price = models.IntegerField()


    def getType(self):
        return self.unit.type







