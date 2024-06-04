from ast import parse
from flask import Blueprint, request, jsonify
from repository.licenciasRepository import newLicense,getLicenses
from datetime import datetime

# Crear instancia Blueprint con el nombre 'licencias'
licencias_bp = Blueprint('licencias', __name__)


@licencias_bp.route('/', methods=['GET'])
def get_licences():
    try:
        result = getLicenses()
        return jsonify(result), 200
    except Exception as e:
        mensaje_error = "Error interno en el servidor: {}".format(str(e))
        return jsonify({'error': mensaje_error}), 500
    
    
@licencias_bp.route('/', methods=['POST'])
def license():
    data = request.form    
    user_id = data.get('user_id')  # Assuming the date is passed as a string
    fechaDesde = data.get('fechaDesde')
    fechaHasta = data.get('fechaHasta')     
    try:
        # Convertir cadenas a objetos datetime con dateutil.parser
        fechaDesde = datetime.strptime(fechaDesde, '%Y-%m-%d')
        fechaHasta = datetime.strptime(fechaHasta, '%Y-%m-%d')
        # Verificar que fechaHasta sea posterior a fechaDesde
        if fechaHasta <= fechaDesde:
            return jsonify({"error": "Fechas incorrectas"}), 400
            # Now you can use horario as a datetime object in your registrarLog function

        # Convertir las fechas al formato deseado
        fechaDesde_str = fechaDesde.strftime('%Y-%m-%d')
        fechaHasta_str = fechaHasta.strftime('%Y-%m-%d')

        resultado = newLicense(user_id,fechaDesde_str,fechaHasta_str)         
        return jsonify(resultado), 200
    except Exception as e:
        # If an error occurs, return a 500 HTTP status code and an error message
        mensaje_error = "Error interno en el servidor: {}".format(str(e))
        return jsonify({'error': mensaje_error}), 500  