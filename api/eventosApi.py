from datetime import datetime
from flask import Blueprint, request, jsonify
from repository.eventosRepository import get_eventos_repository,get_evento_repository, post_eventos_repository, delete_eventos_repository

eventos_bp = Blueprint('eventos', __name__)

@eventos_bp.route('/', methods=['GET'])
def get_eventos():
    params = request.args
    fecha_desde = params.get("fechaDesde")
    fecha_hasta = params.get("fechaHasta")

    if not all([fecha_desde, fecha_hasta]):
      return jsonify({"message": "Indique fechaDesde y fechaHasta"}), 400

    fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d')
    fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d')

    eventos = get_eventos_repository(fecha_desde, fecha_hasta)
    return jsonify(eventos)


@eventos_bp.route('/<evento_id>', methods=['GET'])
def get_evento(evento_id):
    evento = get_evento_repository(evento_id)
    return jsonify(evento), 200 if evento is not None else 404

@eventos_bp.route('/', methods=['DELETE'])
def delete_eventos():
    data = request.json
    _id = data.get("_id")
    if not _id:
      return jsonify({"message": "Please enter valid _id"}), 400

    try:
      deleteResult = delete_eventos_repository(_id)
      return jsonify(deleteResult)
    except Exception as e:
      return jsonify({"message":e.args[0]}), 500
