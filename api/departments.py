from pkg.db.models.repositories import DepartmentsRepo
from pkg.db.schemas.schema import DepartmentsSchema
from pkg.db.db import db
from flask import request

# Departments
deptRepo = DepartmentsRepo()
deptSchema = DepartmentsSchema()
deptListSchema = DepartmentsSchema(many=True)
DEPT_NOT_FOUND = "Departments not found for id: {}"


def get(id):
    dept_data = deptRepo.fetchById(id)
    if dept_data:
        return deptSchema.dump(dept_data)
    return {'message': DEPT_NOT_FOUND.format(id)}, 404


def get_by_university_id(university_id):
    dept_data = deptRepo.fetchByUniversityId(university_id)
    if dept_data:
        return deptSchema.dump(dept_data)
    return {'message': DEPT_NOT_FOUND.format(id)}, 404


def update(id):
    dept_data = deptRepo.fetchById(id)
    dept_req_json = request.get_json()
    if dept_data:
        dept_data.name = dept_req_json['name']
        dept_data.price = dept_req_json['price']
        deptRepo.update(dept_data)
        return deptSchema.dump(dept_data)
    return {'message': DEPT_NOT_FOUND.format(id)}, 404


def delete(id):
    dept_data = deptRepo.fetchById(id)
    if dept_data:
        deptRepo.delete(id)
        return {'message': 'Departments deleted successfully'}, 200
    return {'message': DEPT_NOT_FOUND.format(id)}, 404


def create():
    dept_req_json = request.get_json()
    dept_data = deptSchema.load(dept_req_json, session=db.session)
    deptRepo.create(dept_data)
    return deptSchema.dump(dept_data), 201


def get_all():
    return deptListSchema.dump(deptRepo.fetchAll()), 200
