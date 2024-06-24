from flask import Blueprint, request, jsonify
from repository.reportesRepository import notificarInfoDeSincronizacion
from repository.logsRepository import registrarLog
from repository.usersRepository import chequearExistenciaDeUsuarios
from datetime import datetime, timedelta

reportes_bp = Blueprint('reportes', __name__)
   
@reportes_bp.route('/infoSync', methods=['POST'])
def notificar_info_sincronizacion():
    data=request.json

    try:
        horario_desconexion_str = data.get('horarioDesconexion')  
        horario_reconexion_str = data.get('horarioReconexion')  
        cantRegSincronizados = data.get('cantRegSincronizados')
        periodoDeCorte_str=data.get('periodoDeCorte')
    
      
        horarioDesconexion = datetime.strptime(horario_desconexion_str, '%Y-%m-%d %H:%M:%S')
        horarioReconexion = datetime.strptime(horario_reconexion_str, '%Y-%m-%d %H:%M:%S')

        periodoDeCorte_time = datetime.strptime(periodoDeCorte_str, '%H:%M:%S')
        periodoDeCorte = timedelta(hours=periodoDeCorte_time.hour, minutes=periodoDeCorte_time.minute, seconds=periodoDeCorte_time.second)

        registros = data.get('registros', [])

        resultados = []
        for registro in registros:
            # Convertir el horario de string a datetime
            horario = datetime.strptime(registro['horario'], '%Y-%m-%d %H:%M:%S')
            
            # Llamar a la función que procesa el registro
            resultado = registrarLog(horario, registro['nombre'], registro['apellido'], registro['dni'], registro['estado'], registro['tipo'])
            resultados.append(resultado)

        incompatibles=chequearExistenciaDeUsuarios(registros)
        notificarInfoDeSincronizacion(horarioDesconexion,horarioReconexion,cantRegSincronizados,periodoDeCorte,incompatibles)

        return jsonify(resultados), 200
    except Exception as e:
        mensaje_error = f"Error interno en el servidor: {str(e)}"
        return jsonify({'error': mensaje_error}), 500

    



