from locale import format_string
from goods.models import ShoppingUnit, PriceChange
from django.shortcuts import get_object_or_404
import datetime


class PriceRecord():

    def __init__(self, date, price):
        self.date = date
        self.price = price


    def __lt__(self, other):
        return self.date < other.date


    def __gt__(self, other):
        return self.date > other.date




