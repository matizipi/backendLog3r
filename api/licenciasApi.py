from ast import parse
from flask import Blueprint, request, jsonify
from repository.licenciasRepository import deleteLicencia, newLicense,getLicenses
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
    user_id = data.get('user_id')  
    fechaDesde = data.get('fechaDesde')
    fechaHasta = data.get('fechaHasta')     
    try:
        # Convertir cadenas a objetos datetime con dateutil.parser
        fechaDesde = datetime.strptime(fechaDesde, '%Y-%m-%d')
        fechaHasta = datetime.strptime(fechaHasta, '%Y-%m-%d')
        # Verificar que fechaHasta sea posterior a fechaDesde
        # Obtener el día de la semana de fechaDesde
        dia_semana_fechaDesde = int(fechaDesde.strftime('%w'))
        dia_semana_fechaHasta = int(fechaHasta.strftime('%w'))
        diferencia_dias = ((fechaHasta - fechaDesde).days) +1
        resto = (diferencia_dias) % 7

        if dia_semana_fechaDesde != 1  : 
            return jsonify({"error": "La licencia debe comenzar un lunes"}), 400 
        if dia_semana_fechaHasta !=0 :
            return jsonify({"error": "La licencia debe finalizar un domingo"}), 400 
        if resto!=0:
            return jsonify({"error": "La licencia debe ser multiplo de 7"}), 400
        if diferencia_dias>35 : 
            return jsonify({"error": "La licencia debe ser menor a 35"}), 400 
        if fechaHasta <= fechaDesde:
           return jsonify({"error": "La fecha de inicio debe ser menor a la fin"}), 400          
     

        # Convertir las fechas al formato deseado
        fechaDesde_str = fechaDesde.strftime('%Y-%m-%d')
        fechaHasta_str = fechaHasta.strftime('%Y-%m-%d')

        resultado = newLicense(user_id,fechaDesde_str,fechaHasta_str)         
        return jsonify(resultado), 200
    except Exception as e:
        # If an error occurs, return a 500 HTTP status code and an error message
        mensaje_error = "Error interno en el servidor: {}".format(str(e))
        return jsonify({'error': mensaje_error}), 500  
    

@licencias_bp.route('/<licenciaId>', methods=['DELETE'])
def delete_licencia(licenciaId):
    try:
        result = deleteLicencia(licenciaId)
        return jsonify(result), 200
    except Exception as e:
        mensaje_error = "Error interno en el servidor: {}".format(str(e))
        return jsonify({'error': mensaje_error}), 500    