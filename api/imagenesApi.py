from flask import Blueprint, request, jsonify
from repository.imagenesRepository import get_imagenes_repository, post_imagenes_repository, put_imagenes_repository, delete_imagenes_repository
from repository.usersRepository import get_user_repository

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

    usuario = get_user_repository(userId)
    if not usuario:
        return jsonify({"status": "error", "message": "El usuario ingresado no existe"}), 400

    imagen = post_imagenes_repository(embedding, userId)

    return jsonify(imagen)


@imagenes_bp.route('/api/imagenes', methods=['PUT'])
def put_imagenes():
    data = request.json
    _id = data.get("_id")
    embedding = data.get("embedding")
    userId = data.get("userId")
    if not _id:
        return jsonify({"status": "error", "message": "Please enter valid _id"}), 400

    result = put_imagenes_repository(_id, embedding, userId)

    return jsonify(result)


@imagenes_bp.route('/api/imagenes', methods=['DELETE'])
def delete_imagenes():
    data = request.json
    _id = data.get("_id")
    if not _id:
        return jsonify({"status": "error", "message": "Please enter valid _id"}), 400
    result = delete_imagenes_repository(_id)
    return jsonify(result)
