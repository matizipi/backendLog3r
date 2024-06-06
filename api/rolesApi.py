from flask import Blueprint, request, jsonify
from repository.rolesRepository import get_roles_repository, post_roles_repository, put_roles_repository, delete_roles_repository

roles_bp = Blueprint('roles', __name__)

@roles_bp.route('/', methods=['GET'])
def get_roles():
    params = request.args
    role_id = params.get("_id")
    roles = get_roles_repository(role_id)

    return jsonify(roles)

@roles_bp.route('/', methods=['POST'])
def post_roles():
    data = request.json
    new_role_name = data.get("nombre")
    new_lugares = data.get("lugares")

    try:
      validateNameAndLugares(new_role_name, new_lugares)
    except Exception as e:
      return jsonify({"status":"error","message":e.args[0]}), 400

    try:
      new_role = post_roles_repository(new_role_name, new_lugares)
      return jsonify(new_role), 201
    except Exception as e:
      return jsonify({"status":"error","message":e.args[0]}), 500


@roles_bp.route('/', methods=['PUT'])
def put_roles():
    data = request.json
    _id = data.get("_id")
    if not _id:
      return jsonify({"message": "Please enter valid _id"}), 400

    new_role_name = data.get("nombre")
    new_lugares = data.get("lugares")
    try:
      validateNameAndLugares(new_role_name, new_lugares)
    except Exception as e:
      return jsonify({"message":e.args[0]}), 400

    try:
      updateResult = put_roles_repository(_id, new_role_name, new_lugares)
      return jsonify(updateResult)
    except Exception as e:
      return jsonify({"message":e.args[0]}), 500


@roles_bp.route('/', methods=['DELETE'])
def delete_roles():
    data = request.json
    _id = data.get("_id")
    if not _id:
      return jsonify({"message": "Please enter valid _id"}), 400

    try:
      deleteResult = delete_roles_repository(_id)
      return jsonify(deleteResult)
    except Exception as e:
      return jsonify({"message":e.args[0]}), 500


def validateNameAndLugares(role_name, lugares):
    if not role_name:
      raise RuntimeError('Please enter valid nombre')
        
    if not lugares or not type(lugares) is list:
      raise RuntimeError('lugares must be an array')
      
    if not all(isinstance(lugar, str) for lugar in lugares):
      raise RuntimeError('All lugares must be string elements')