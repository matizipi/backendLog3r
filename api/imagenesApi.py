from flask import Blueprint, request, jsonify
from repository.imagenesRepository import get_imagenes_repository, post_imagenes_repository
from repository.usuariosRepository import get_usuario_repository

imagenes_bp = Blueprint('imagenes', __name__)


@imagenes_bp.route('/api/imagenes', methods=['GET'])
def get_imagenes():
    params = request.args
    user_id = params.get("userId")
    if not user_id:
        return jsonify({"status": "error", "message": "Please enter valid userId"}), 400
    imagenes = get_imagenes_repository(user_id)

    return jsonify(imagenes)


@imagenes_bp.route('/api/imagenes', methods=['POST'])
def post_imagenes():
    data = request.json
    embedding = data.get("embedding")
    userId = data.get("userId")
    # if not embedding or len(embedding) != 192:
    if not embedding:
        return jsonify({"status": "error", "message": "Please enter valid embedding"}), 400
    if not userId:
        return jsonify({"status": "error", "message": "Please enter valid userId"}), 400

    usuario = get_usuario_repository(userId)
    if not usuario:
        return jsonify({"status": "error", "message": "El usuario ingresado no existe"}), 400

    imagen = post_imagenes_repository(embedding, userId)

    return jsonify(imagen)


@imagenes_bp.route('/api/imagenes', methods=['PUT'])
def put_imagenes():
    data = request.json
    return jsonify({"message": "PUT request for imagenes", "data": data})


@imagenes_bp.route('/api/imagenes', methods=['DELETE'])
def delete_imagenes():
    return jsonify({"message": "DELETE request for imagenes"})
