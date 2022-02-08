from pkg.db.db import ma
from pkg.db.models.entities import Item, Departments


class ItemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Item
        load_instance = True


class DepartmentsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Departments
        load_instance = True
