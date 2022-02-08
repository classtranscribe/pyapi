from pkg.db.db import db
from pkg.db.models.entities import Item, Departments
from typing import List


class ItemRepo:

    def create(self, item):
        db.session.add(item)
        db.session.commit()

    def fetchById(self, _id) -> 'Item':
        return db.session.query(Item).filter_by(id=_id).first()

    def fetchAll(self) -> List['Item']:
        return db.session.query(Item).all()

    def delete(self, _id) -> None:
        item = db.session.query(Item).filter_by(id=_id).first()
        db.session.delete(item)
        db.session.commit()

    def update(self, item_data):
        db.session.merge(item_data)
        db.session.commit()


class DepartmentsRepo:

    def create(self, dept):
        db.session.add(dept)
        db.session.commit()

    def fetchByUniversityId(self, _id) -> 'Departments':
        return db.session.query(Departments).filter_by(UniversityId=_id).first()

    def fetchById(self, _id) -> 'Departments':
        return db.session.query(Departments).filter_by(Id=_id).first()

    def fetchAll(self) -> List['Departments']:
        return db.session.query(Departments).all()

    def delete(self, _id) -> None:
        dept = db.session.query(Departments).filter_by(Id=_id).first()
        db.session.delete(dept)
        db.session.commit()

    def update(self, dept_data):
        db.session.merge(dept_data)
        db.session.commit()

