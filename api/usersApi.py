from flask import Blueprint, request, jsonify
from repository.usersRepository import get_users_repository, get_user_repository, create_user_repository, update_user_repository, delete_user_repository
users_bp = Blueprint('users', __name__)

@users_bp.route('', methods=['GET'])
def get_users():
    try:
        result = get_users_repository()
        return jsonify(result), 200
    except Exception as e:
        mensaje_error = "Error interno en el servidor: {}".format(str(e))
        return jsonify({'error': mensaje_error}), 500

@users_bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = get_user_repository(user_id)
        return jsonify(user if user is not None else {})

    except Exception as e:
        mensaje_error = "Error interno en el servidor: {}".format(str(e))
        return jsonify({'error': mensaje_error}), 500


@users_bp.route('', methods=['POST'])
def create_user():
    data = request.json
    try:
        nombre = data.get('nombre')
        apellido = data.get('apellido')
        dni = data.get('dni')
        rol = data.get('rol')
        horarios = data.get('horarios')
        email = data.get('email')

        # Validar campos requeridos
        if not all([nombre, apellido, dni, rol, horarios]):
            return jsonify({"error": "Faltan datos obligatorios"}), 400

        # horarios_splitted = horarios.split('-')
        
        new_user = create_user_repository(nombre, apellido, dni, rol, horarios, email)
        return jsonify(new_user)
        # return jsonify(result), 200
    except RuntimeError as e:
        return jsonify({'message': e.args[0]}), 400
    except Exception as e:
        mensaje_error = "Error interno en el servidor: {}".format(str(e))
        return jsonify({'message': mensaje_error}), 500


@users_bp.route('/<user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    try:
        nombre = data.get('nombre')
        apellido = data.get('apellido')
        dni = data.get('dni')
        rol = data.get('rol')
        horarios = data.get('horarios')
        email = data.get('email')

        # Validar campos requeridos
        if not all([nombre, apellido, dni, rol, horarios]):
            return jsonify({"error": "Faltan datos obligatorios"}), 400

        result = update_user_repository(user_id, nombre, apellido, dni, rol, horarios, email)
        return jsonify({'mensaje': 'Usuario actualizado' if result['modifiedCount'] > 0 else 'No se realizaron cambios'}), 200
    except RuntimeError as e:
        return jsonify({'error': e.args[0]}), 400
    except Exception as e:
        mensaje_error = "Error interno en el servidor: {}".format(str(e))
        return jsonify({'error': mensaje_error}), 500



@users_bp.route('/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        result = delete_user_repository(user_id)
        return jsonify({'mensaje': 'Usuario eliminado' if result['deletedCount'] > 0 else 'Usuario no encontrado'}), 200
    except Exception as e:
        mensaje_error = "Error interno en el servidor: {}".format(str(e))
        return jsonify({'error': mensaje_error}), 500
