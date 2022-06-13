from distutils.command.build import build
from unicodedata import category
from urllib import response
from urllib.request import Request
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.request import Request
from goods.unit import Category, Offer, Unit, ShoppingUnitAdapter, PriceRecord
import json
import datetime
from goods.models import ShoppingUnit, PriceChange
from django.core.serializers.json import DjangoJSONEncoder

class DateValidator:
    format_string = '%Y-%m-%dT%H:%M:%S.%f%z'

    @staticmethod
    def validateDateString(date_string):
        return datetime.datetime.strptime(date_string, DateValidator.format_string)






class Imports(APIView):
    response400 = JsonResponse({
                      "code": 400,
                      "message": "Validation Failed"
                    }, status=400)


    def post(self, request, format=None):   #offer and category to one array
        try:
            items = request.data['items']
            update_date = DateValidator.validateDateString(request.data['updateDate'])

            
            offers = []
            categories = []
            uuids = []
            for item in items:
                if item['type'] == 'OFFER':
                    offers.append(Offer(item['id'], item['name'], item.get('parentId', None), update_date, item['price']))
                    if not offers[-1].check():
                        raise Exception("Validation failed")
                elif item['type'] == 'CATEGORY':
                    categories.append(Category(item['id'], item['name'], item.get('parentId', None), update_date))
                    if item.get('price', None) is not None:
                        raise Exception("Validation failed")
                    if not categories[-1].check():
                        raise Exception("Validation failed")
                else:
                    raise Exception("Validation failed")
                if item['id'] in uuids:
                    raise Exception("Validation failed")
                else:
                    uuids.append(item['id'])

            new_categories_uuid = set()
            for category in categories:
                if category.new:
                    new_categories_uuid.add(category.id)
            for category in categories:
                if category.parent_new:
                    if category.parent_id not in new_categories_uuid:
                        raise Exception("Validation failed")
            for offer in offers:
                if offer.parent_new:
                    if offer.parent_id not in new_categories_uuid:
                        raise Exception("Validation failed")
            
            delta = 1
            while len(categories) + len(offers) > 0 and delta > 0:  #think???
                for category in categories:
                    if not category.parent_new:
                        category.saveModel()
                        print(category.saved)
                for offer in offers:
                    if not offer.parent_new:
                        offer.saveModel()
                delta = len(categories) + len(offers)
                categories = list(filter(lambda category: category.saved == False, categories))
                offers = list(filter(lambda offer: offer.saved == False, offers))
                delta -= len(categories) + len(offers)
                for category in categories:
                    category.check_parent()
                for offer in offers:
                    offer.check_parent()
            if len(categories) + len(offers) == 0:
                return HttpResponse(status=200)
            else:
                return Imports.response400
        except Exception:
            return Imports.response400


            
            
class Delete(APIView):
    response404 = JsonResponse({
                      "code": 404,
                      "message": "Item not found"
                    }, status=404)


    def delete(self, request, id, format=None):
        if ShoppingUnit.objects.filter(pk=id).exists():
            ShoppingUnitAdapter.delete(id)
            return HttpResponse(status=200)
        else:
            return Delete.response404


class Nodes(APIView):

    response404 = JsonResponse({
                      "code": 404,
                      "message": "Item not found"
                    }, status=404)


    def get(self, request, id = "not_valid", format=None):
        try:
            instance = Unit.buildFromModel(ShoppingUnit.objects.get(pk=id))
            dict = instance.json_build()
            return JsonResponse(dict)
        except ShoppingUnit.DoesNotExist:
            return Nodes.response404


class DeleteEmpty(APIView):
    def delete(self, request, format=None):
        return JsonResponse({
                      "code": 400,
                      "message": "Validation Failed"
                    }, status=400)


class NodesEmpty(APIView):
    def get(self, request, format=None):
        return JsonResponse({
                      "code": 400,
                      "message": "Validation Failed"
                    }, status=400)

class Sales(APIView):
    response400 = JsonResponse({
                      "code": 400,
                      "message": "Validation Failed"
                    }, status=400)

    def get(self, request, format=None):
        try:
            date_string_end = request.GET["date"]
        except KeyError:
            return Sales.response400
        date_end = DateValidator.validateDateString(date_string_end)
        date_begin = date_end - datetime.timedelta(days=1)
        unit_list = ShoppingUnit.objects.filter(date__range=[date_begin, date_end], type="OFFER")
        price_change = PriceChange.objects.filter(date__range=[date_begin, date_end])
        price_change = list(filter(lambda record: record.getType == "OFFER", price_change))
        result_list = []
        for item in unit_list:
            item_dict = {item.id : Unit.dateToString(item.date)}
            result_list.append(item_dict)
        for item in price_change:
            item_dict = {item.id : Unit.dateToString(item.date)}
            result_list.append(item_dict)
        return(JsonResponse({"objects": result_list}, status=200))


class NodeStatistic(APIView):
    response400 = JsonResponse({
                      "code": 400,
                      "message": "Validation Failed"
                    }, status=400)


    response404 = JsonResponse({
                      "code": 404,
                      "message": "Item not found"
                    }, status=404)

    def get(self, request, id, format=None):
        try:
            dateStart = DateValidator.validateDateString(request.GET["dateStart"])
            dateEnd = DateValidator.validateDateString(request.GET["dateEnd"])
        except KeyError:
            return NodeStatistic.response400
        try:
            unit = ShoppingUnit.objects.filter(pk=id)[0]
        except IndexError:
            return NodeStatistic.response404
        price_change = PriceChange.objects.filter(unit=unit)
        price_records = []
        price_records.append(PriceRecord(unit.date, unit.price))
        for record in price_change:
            price_records.append(PriceRecord(record.date, record.price))
        price_records = list(filter(lambda price_record: price_record.date <= dateEnd, price_records))
        price_records_before = list(filter(lambda price_record: price_record.date <= dateStart, price_records))
        price_records = list(filter(lambda price_record: price_record.date > dateStart, price_records))
        result_list = []
        if len(price_records_before) > 0:
            first_record = max(price_records_before)
            result_list.append({Unit.dateToString(first_record) : first_record.price})
        for record in price_records:
            result_list.append({Unit.dateToString(record.date) : record.price})
        json_dict = {"data" : result_list}
        return JsonResponse(json_dict)





