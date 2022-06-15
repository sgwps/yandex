from distutils.command.build import build
from unicodedata import category
from urllib import response
from urllib.request import Request
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.request import Request
from goods.unit import PriceRecord
import json
import datetime
from goods.models import ShoppingUnit, PriceChange
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import get_object_or_404
from goods.date_validator import DateValidator
from goods.import_schema import ImportSchema








class Imports(APIView):
    response400 = JsonResponse({
                      "code": 400,
                      "message": "Validation Failed"
                    }, status=400)


    def post(self, request, format=None):   
        try:
            schema = ImportSchema()
            import_schema = schema.load(request.data)
            items = import_schema['items']
            saved_categories = set()
            while items: 
                for item in items:
                    if not item.get('parent_new', False) or item['parentId'] in saved_categories:
                        ShoppingUnit.save_import(item, import_schema['updateDate'])
                        item['saved'] = True
                        if item['type'] == 'CATEGORY':
                            saved_categories.add(item['id'])

                items = list(filter(lambda item: item.get('saved')==None, items))

            return HttpResponse(status=200)
            
        except Exception as e:
            return Imports.response400


            
            
class Delete(APIView):
    response404 = JsonResponse({
                      "code": 404,
                      "message": "Item not found"
                    }, status=404)


    def delete(self, request, id, format=None):
        try:
            unit = get_object_or_404(ShoppingUnit, pk=id)
            unit.custom_delete()
            return HttpResponse(status=200)
        except Exception:
            return Delete.response404


class Nodes(APIView):

    response404 = JsonResponse({
                      "code": 404,
                      "message": "Item not found"
                    }, status=404)


    def get(self, request, id = "not_valid", format=None):
        try:
            instance = get_object_or_404(ShoppingUnit, pk=id)
            return JsonResponse(instance.json_build())
        except Exception:
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
            date_end = DateValidator.validateDateString(request.GET["date"])

        except KeyError:
            return Sales.response400
        date_begin = date_end - datetime.timedelta(days=1)
        unit_list = ShoppingUnit.objects.filter(date__range=[date_begin, date_end], type="OFFER")
        price_change = PriceChange.objects.filter(date__range=[date_begin, date_end])
        price_change = list(filter(lambda record: record.getType == "OFFER", price_change))
        result_list = []
        for i in (unit_list, price_change):
            for item in i:
                item_dict = {item.id : DateValidator.dateToString(item.date)}
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
            unit = get_object_or_404(ShoppingUnit, pk=id)
        except Exception:
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
        if price_records_before:
            first_record = max(price_records_before)
            result_list.append({DateValidator.dateToString(first_record) : first_record.price})
        for record in price_records:
            result_list.append({DateValidator.dateToString(record.date) : record.price})
        json_dict = {"data" : result_list}
        return JsonResponse(json_dict)
