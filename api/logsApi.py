from flask import Blueprint, request, jsonify
from repository.logsRepository import obtener_logs_dia_especifico, registrarLog
from repository.usersRepository import get_last_estado_by_dni, chequearExistenciaDeUsuario
from datetime import datetime

# Crear instancia Blueprint con el nombre 'logs'
logs_bp = Blueprint('logs', __name__)

@logs_bp.route('/', methods=['GET'])
def get_logs():
    fecha_str = request.args.get('fecha')
    if not fecha_str:
        return jsonify({'error': 'Falta el parámetro fecha'}), 400

    try:
        # Convertir la fecha de cadena a objeto datetime
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
        print(f"Fecha recibida: {fecha}")  # Depuración
        result = obtener_logs_dia_especifico(fecha)
        return jsonify(result), 200  # Asegurar que se devuelve como JSON
    except Exception as e:
        mensaje_error = "Error interno en el servidor: {}".format(str(e))
        return jsonify({'error': mensaje_error}), 500

@logs_bp.route('/day', methods=['GET'])
def get_logs_dia():
    fecha_str = request.args.get('fecha')
    if not fecha_str:
        return jsonify({'error': 'Falta el parámetro fecha'}), 400

    try:
        # Convertir la fecha de cadena a objeto datetime
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
        print(f"Fecha recibida: {fecha}")  # Depuración
        result = obtener_logs_dia_especifico(fecha)
        return jsonify(result), 200  # Asegurar que se devuelve como JSON
    except Exception as e:
        mensaje_error = "Error interno en el servidor: {}".format(str(e))
        return jsonify({'error': mensaje_error}), 500

@logs_bp.route('/authentication', methods=['POST'])
def log_authentication():
    data = request.form
    horario_str = data.get('horario')  # Assuming the date is passed as a string
    nombre = data.get('nombre')
    apellido = data.get('apellido')
    dni = data.get('dni')
    estado = data.get('estado')
    tipo = data.get('tipo')

    try:
        # Convert string to datetime object
        horario = datetime.strptime(horario_str, '%Y-%m-%d %H:%M:%S')  # Adjust the format if necessary       

        # Now you can use horario as a datetime object in your registrarLog function
        resultado = registrarLog(horario, nombre, apellido, dni, estado, tipo)

        return jsonify(resultado), 200
    except Exception as e:
        # If an error occurs, return a 500 HTTP status code and an error message
        mensaje_error = "Error interno en el servidor: {}".format(str(e))
        return jsonify({'error': mensaje_error}), 500
    
@logs_bp.route('/lastEstadoByDni', methods=['GET'])
def get_last_estado():
    dni = request.args.get('dni')
    if not dni:
        return jsonify({'error': 'Falta el parámetro dni'}), 400

    response, status_code = get_last_estado_by_dni(dni)  # Obtener la respuesta y el código de estado
    return jsonify(response), status_code  # Devolver la respuesta y el código de estado



@logs_bp.route('/authenticationOffline', methods=['POST'])
def log_authentication_Offline():
    data = request.form
    horario_str = data.get('horario')  # Assuming the date is passed as a string
    nombre = data.get('nombre')
    apellido = data.get('apellido')
    dni = data.get('dni')
    estado = data.get('estado')
    tipo = data.get('tipo')

    try:
        # Convert string to datetime object
        horario = datetime.strptime(horario_str, '%Y-%m-%d %H:%M:%S')  # Adjust the format if necessary       

        # Now you can use horario as a datetime object in your registrarLog function
        resultado = registrarLog(horario, nombre, apellido, dni, estado, tipo)
        chequearExistenciaDeUsuario(nombre,apellido,dni)

        return jsonify(resultado), 200
    except Exception as e:
        # If an error occurs, return a 500 HTTP status code and an error message
        mensaje_error = "Error interno en el servidor: {}".format(str(e))
        return jsonify({'error': mensaje_error}), 500