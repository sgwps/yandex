from locale import format_string
from goods.models import ShoppingUnit, PriceChange
from django.shortcuts import get_object_or_404
import datetime

class ShoppingUnitAdapter():
    @staticmethod
    def update(instance_unit, unit_model):
        price_change = PriceChange(unit=unit_model, date=unit_model.date, price=unit_model.get_price)
        price_change.save()
        unit_model.name = instance_unit.name
        unit_model.date = instance_unit.date
    
        if instance_unit.price is not None:
            unit_model.price = instance_unit.price
        if instance_unit.parent_id is not None:
            unit_model.parentId = get_object_or_404(ShoppingUnit, pk=instance_unit.parent_id)
            unit_model.save() 
            unit_model.parentId.check_children()
        else:
            unit_model.save()

    @staticmethod
    def create(instance_unit):
        unit = ShoppingUnit()
        unit.id = instance_unit.id
        unit.name = instance_unit.name
        unit.date = instance_unit.date
        
        unit.type = type(instance_unit).strtype
        if unit.type == "OFFER":
            unit.price = instance_unit.price
            unit.amount = 1
        else:
            unit.price = 0
            unit.amount = 0
        unit.save()
        if instance_unit.parent_id is not None:
            unit.parentId = get_object_or_404(ShoppingUnit, pk=instance_unit.parent_id)
            unit.save()
            unit.parentId.check_children()
        if unit.parentId is not None:
            unit.save()


    @staticmethod
    def update_or_create(instance_unit):
        try:
            unit = get_object_or_404(ShoppingUnit, pk=instance_unit.id)
            ShoppingUnitAdapter.update(instance_unit, unit)
        except Exception:
            ShoppingUnitAdapter.create(instance_unit)



class Unit:
    


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
        '''
        True - element is new
        False - element is recorded in DB
        '''
        try:
            unit = ShoppingUnit.objects.get(pk=self.id)
            if unit.type == type(self).strtype:
                self.new = False
            else:
                raise Exception("Unit category cannot be changed")
        except ShoppingUnit.DoesNotExist:
            self.new = True


    def check_parent(self):
        '''
        -1 - unit doesn't have a parent
        0 - parent is an existing category
        1 - parent is potentially new
        '''
        if self.parent_id is not None:
            try:
                unit = get_object_or_404(ShoppingUnit, pk=self.parent_id)
                if unit.type == Category.strtype:
                    self.parent_flag = 0
                elif unit.type == Offer.strtype:
                    raise Exception("Parent is an existing offer")
            except Exception:
                self.parent_flag = 1
        else:
            self.parent_flag = -1


    def validate(self):
        self.check_parent()
        self.check_newness()





class Offer(Unit):

    strtype = "OFFER"

    def check_price(self):
        if not isinstance(self.price, int):
            raise Exception("Offer price must be an integer")
        elif self.price < 0:
            raise Exception("Offer price cannot be less than 0")


    def validate(self):
        super().validate()
        self.check_price()


class Category(Unit):   

    strtype = "CATEGORY"




class PriceRecord():

    def __init__(self, date, price):
        self.date = date
        self.price = price


    def __lt__(self, other):
        return self.date < other.date


    def __gt__(self, other):
        return self.date > other.date




