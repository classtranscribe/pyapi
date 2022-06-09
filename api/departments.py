import logging

from pkg.db.models.repositories import DepartmentsRepo
from pkg.db.schemas.schema import DepartmentsSchema
from pkg.db.db import db
from flask import request
from pkg.agent.rabbitpy_wrapper import rabbitpy_emitter as agent
from pkg import jwt

# Departments
deptRepo = DepartmentsRepo()
deptSchema = DepartmentsSchema()
deptListSchema = DepartmentsSchema(many=True)
DEPT_NOT_FOUND = "Departments not found for id: {}"

logger = logging.getLogger('api.departments')


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
    return save(id, request.get_json())


def save(id, updated):
    dept_data = deptRepo.fetchById(id)
    if dept_data:
        dept_data.name = updated['name']
        dept_data.price = updated['price']
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


def publish_test_message():
    # example video id
    video_id = '7fc3b0a5-ae81-4a46-b369-d3fb14eb0866'
    # video_id = 'f6bce30b-d5d5-462c-a74d-e56ece954ca8'

    # all tasks should have the same body structure
    body = {
        'Data': video_id,
        # 'Data': 'db2090f7-09f2-459a-84b9-96bd2f506f68',
        'TaskParameters': {'Force': True, 'Metadata': None, 'ReadOnly': False}
    }

    try:
        agent.publish(body=body, routing_key="SceneDetection")
    except Exception as e:
        logger.error("Failed to publish message: " + str(e))

    return body, 200


