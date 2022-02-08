from pkg.db.models.repositories import ItemRepo
from pkg.db.schemas.schema import ItemSchema
from pkg.db.db import db
from flask import request

# Item (basic example)
itemRepo = ItemRepo()
itemSchema = ItemSchema()
itemListSchema = ItemSchema(many=True)
ITEM_NOT_FOUND = "Item not found for id: {}"


def get(id):
    item_data = itemRepo.fetchById(id)
    if item_data:
        return itemSchema.dump(item_data)
    return {'message': ITEM_NOT_FOUND.format(id)}, 404


def update(id):
    item_data = itemRepo.fetchById(id)
    item_req_json = request.get_json()
    if item_data:
        item_data.name = item_req_json['name']
        item_data.price = item_req_json['price']
        itemRepo.update(item_data)
        return itemSchema.dump(item_data)
    return {'message': ITEM_NOT_FOUND.format(id)}, 404


def delete(id):
    item_data = itemRepo.fetchById(id)
    if item_data:
        itemRepo.delete(id)
        return {'message': 'Item deleted successfully'}, 200
    return {'message': ITEM_NOT_FOUND.format(id)}, 404


def create():
    item_req_json = request.get_json()
    item_data = itemSchema.load(item_req_json, session=db.session)
    itemRepo.create(item_data)
    return itemSchema.dump(item_data), 201


def get_all():
    return itemListSchema.dump(itemRepo.fetchAll()), 200

