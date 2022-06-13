from locale import format_string
from goods.models import ShoppingUnit, PriceChange
import datetime

class ShoppingUnitAdapter():
    @staticmethod
    def update(instance_unit):
        unit_model = ShoppingUnit.objects.filter(pk=id)[0]
        price_change = PriceChange(unit=unit_model, date=unit_model.date, price=unit_model.get_price)
        price_change.save()
        unit_model.name = instance_unit.name
        unit_model.date = instance_unit.date
        if instance_unit.parent_id is not None:
            unit_model.parent = ShoppingUnit.objects.filter(pk=instance_unit.parent)[0] 
        if instance_unit.price is not None:
            unit_model.price = instance_unit.price
        unit_model.save()
        ShoppingUnit.objects.filter(pk=instance_unit.parent)[0].check_children()

    @staticmethod
    def create(instance_unit):
        unit = ShoppingUnit()
        unit.id = instance_unit.id
        unit.name = instance_unit.name
        unit.date = instance_unit.date
        if instance_unit.parent_id is not None:
            unit.parentId = ShoppingUnit.objects.filter(pk=instance_unit.parent_id)[0]
        unit.type = type(instance_unit).strtype
        if unit.type == "OFFER":
            unit.price = instance_unit.price
            unit.amount = 1
        else:
            unit.price = 0
            unit.amount = 0
        print(unit, "saving")
        unit.save()
        if unit.parentId is not None:
            ShoppingUnit.objects.filter(pk=instance_unit.parent_id)[0].check_children()

    @staticmethod
    def update_or_create(instance_unit):
        if ShoppingUnit.objects.filter(pk=id).exists():
            ShoppingUnitAdapter.update(instance_unit)
        else:
            ShoppingUnitAdapter.create(instance_unit)


    
    @staticmethod
    def delete(id):
        unit_model = ShoppingUnit.objects.filter(pk=id)[0]
        parent = unit_model.parentId
        unit_model.delete()
        if parent is not None:
            parent.check_children()


class Unit:
    format_string = '%Y-%m-%dT%H:%M:%S.%f'


    @staticmethod
    def dateToString(date):
        print(date)
        return date.strftime(Unit.format_string)[:-3] + "Z"


    def __init__(self, id, name, parent_id, date = None, price = 0):
        self.id = id
        self.name = name
        self.parent_id = parent_id
        self.parent_new = False
        self.new = False
        self.saved = False
        self.date = date
        self.price = price


    @staticmethod
    def buildFromModel(shopping_unit : ShoppingUnit):
        parentId = None
        if shopping_unit.parentId is not None:
            parentId = shopping_unit.parentId.id
        if shopping_unit.type == "OFFER":
            return Offer(shopping_unit.id, shopping_unit.name, parentId, shopping_unit.date, shopping_unit.get_price())
        else:
            return Category(shopping_unit.id, shopping_unit.name, parentId, shopping_unit.date, shopping_unit.get_price())
        

    def saveModel(self):
        ShoppingUnitAdapter.update_or_create(self)
        self.saved = True


    def check_newness(self):
        unit_list = ShoppingUnit.objects.filter(pk=self.id)
        if len(unit_list) > 0:
            if unit_list[0].type != type(self).strtype:
                return False
        else:
            self.new = True
        return True


    def check_parent(self):
        self.parent_new = False
        if self.parent_id is not None:
            unit_list = ShoppingUnit.objects.filter(pk=self.parent_id)
            if len(unit_list) > 0:
                if ShoppingUnit.objects.filter(pk=self.parent_id)[0].type == Offer.strtype:
                    return False
            else:
                self.parent_new = True
        return True


    def json_build(self):
        json_dict = dict()
        json_dict['id'] = self.id
        json_dict['name'] = self.name
        json_dict['date'] = Unit.dateToString(self.date)
        json_dict['type'] = type(self).strtype
        json_dict['price'] = self.price
        if self.price == 0 and type(self).strtype == "CATEGORY":
            json_dict['price'] = None
        if self.parent_id is not None:
            json_dict['parentId'] = self.parent_id
        else:
            json_dict['parentId'] = None
        model_instance = ShoppingUnit.objects.filter(pk=self.id)[0]
        children = ShoppingUnit.objects.filter(parentId = model_instance)
        if len(children) > 0:
            json_dict['children'] = []
            for item in children:
                instance = Unit.buildFromModel(item)
                json_dict['children'].append(instance.json_build())
        else:
            json_dict['children'] = None
        return json_dict


class Offer(Unit):

    strtype = "OFFER"

    def check_price(self):
        if not isinstance(self.price, int):
            return False
        elif self.price < 0:
            return False
        return True


    def check(self):
        if self.check_newness() and self.check_parent() and self.check_price():
            return True
        return False


class Category(Unit):   

    strtype = "CATEGORY"


    def check(self):
        if self.check_newness() and self.check_parent():
            return True
        return False



class PriceRecord():

    def __init__(self, date, price):
        self.date = date
        self.price = price


    def __lt__(self, other):
        return self.date < other.date


    def __gt__(self, other):
        return self.date > other.date




