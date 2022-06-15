from datetime import date
from email.policy import default
from urllib import request
from attr import validate
from django.shortcuts import get_object_or_404
from goods.models import ShoppingUnit
from goods.date_validator import DateValidator

from marshmallow import Schema, fields, validates_schema, ValidationError
from marshmallow.fields import DateTime, Dict, Float, Int, List, Nested, Str, Bool
from marshmallow.validate import OneOf, Range


class ItemSchema(Schema):
    id = Str(required=True)
    name = Str(required=True)
    parentId = Str(required=False, allow_none=True)
    type = Str(validate=OneOf(["OFFER", "CATEGORY"]), required=True)
    price = Int(required=False, validate=Range(min=0, min_inclusive=True), allow_none=True, strict=True)
    parent_new = Bool(required=False, default=False, allow_none=True)

    @validates_schema
    def validate_category_price(self, data, **_):
        if data['type'] == 'CATEGORY':
            if data.get('price'):
                raise ValidationError(
                        'Category %r has price as an attribute' % data['id']
                    )
        elif data['type'] == 'OFFER':
            if data['price'] is None:
                raise ValidationError(
                        'Offer %r does not have price as an attribute' % data['id']
                    )


    @validates_schema
    def validate_newness(self, data, **_):
        try:
            self_type = ShoppingUnit.objects.get(pk=data['id']).type
            if self_type != data['type']:
                raise ValidationError(
                    'Item %r category cannot be changed' % data['id']
                )
        except ShoppingUnit.DoesNotExist:
            pass


class ImportSchema(Schema):
    updateDate = DateTime(required=True, format=DateValidator.format_string)
    items = Nested(ItemSchema, many=True, required=True)

    @validates_schema
    def validate_unique_item_id(self, data, **_):
        items_ids = set()
        for item in data['items']:
            if item['id'] in items_ids:
                raise ValidationError(
                    'item id %r is not unique' % item['id']
                )
            items_ids.add(item['id'])


    @validates_schema
    def validate_parents(self, data, **_):
        categories_ids = set()
        for item in data['items']:
            if item['type'] == 'CATEGORY':
                categories_ids.add(item['id'])
        for item in data['items']:
            if item.get('parentId'):
                try:
                    parent_type = ShoppingUnit.objects.get(pk=item['parentId']).type
                    if parent_type == "OFFER":
                        raise ValidationError(
                            'Parent cannot be validated for %r' % item['id']
                        )
                except ShoppingUnit.DoesNotExist:
                    if not(item['parentId'] in categories_ids):
                        raise ValidationError(
                            'Parent cannot be validated for %r' % item['id']
                        )
                    item['parent_new'] = True
