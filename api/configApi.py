import numbers
from flask import Blueprint, request, jsonify
from repository.configRepository import get_config_repository, post_config_repository, put_config_repository, delete_config_repository
from comparacionCaras import setTHRESHOLD

config_bp = Blueprint('configuraciones', __name__)

@config_bp.route('/', methods=['GET'])
def get_configuraciones():
    params = request.args
    config_name = params.get("nombre")
    configuraciones = get_config_repository(config_name)

    return jsonify(configuraciones)

@config_bp.route('/', methods=['POST'])
def post_configuraciones():
    data = request.json
    config_name = data.get("nombre")
    new_value = data.get("valor")

    try:
      validateNameAndValue(config_name, new_value)
        
    except Exception as e:
      return jsonify({"status":"error","message":e.args[0]}), 400

    try:
      new_config = post_config_repository(config_name, new_value)
      return jsonify(new_config), 201

    except RuntimeError as e:
      return jsonify({"status":"error","message":e.args[0]}), 400
    except Exception as e:
      return jsonify({"status":"error","message":e.args[0]}), 500

@config_bp.route('/', methods=['PUT'])
def put_configuraciones():
    data = request.json
    
    new_config_name = data.get("nombre")
    new_value = data.get("valor")
    try:
      validateNameAndValue(new_config_name, new_value)
    except Exception as e:
      return jsonify({"message":e.args[0]}), 400

    try:
      updateResult = put_config_repository(new_config_name, new_value)
      if new_config_name == 'certeza':
        setTHRESHOLD(new_value)

      return jsonify(updateResult)
    except Exception as e:
      return jsonify({"message":e.args[0]}), 500


@config_bp.route('/', methods=['DELETE'])
def delete_configuraciones():
    data = request.json
    nombre = data.get("nombre")
    if not nombre or not isinstance(nombre, str):
      return jsonify({"message": "Please enter valid nombre"}), 400
    
    if nombre == 'certeza' or nombre == 'bloquear ingreso':
      return jsonify({"message":"can not delete that config"}), 400


    try:
      deleteResult = delete_config_repository(nombre)
      return jsonify(deleteResult)
    except Exception as e:
      return jsonify({"message":e.args[0]}), 500


def validateNameAndValue(config_name, value):
    if not config_name or not isinstance(config_name, str):
      raise RuntimeError('Please enter a valid "nombre"')
    
    if config_name == 'certeza':
      if not isinstance(value, numbers.Number) or value < 0 or value > 1:
        raise RuntimeError('value must be a number between 0 and 1 for config "certeza"')

    elif config_name == 'bloquear ingreso':  
      if not isinstance(value, bool):
        raise RuntimeError('value must be a boolean for config "bloquear ingreso"')