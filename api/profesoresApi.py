from flask import Blueprint,jsonify
from repository.profesoresRepository import getTeachers

# Crear instancia Blueprint con el nombre 'profesores'
profesores_bp = Blueprint('profesores', __name__)


@profesores_bp.route('/', methods=['GET'])
def get_teachers():
    try:
        result = getTeachers()
        return jsonify(result), 200
    except Exception as e:
        mensaje_error = "Error interno en el servidor: {}".format(str(e))
        return jsonify({'error': mensaje_error}), 500   