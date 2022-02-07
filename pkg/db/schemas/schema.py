from pkg.db.db import ma
from pkg.db.models.entities import Item


class ItemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Item
        load_instance = True