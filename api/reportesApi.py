from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from repository.reportesRepository import notificarCorte
import os
from bson import ObjectId
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from database.connection import db

reportes_bp = Blueprint('reportes', __name__)

@reportes_bp.route('/cortes', methods=['POST'])
def notificar_cortes_conexion():
    data = request.form    
    horario_desconexion_str = data.get('horarioDesconexion')  
    horario_reconexion_str = data.get('horarioReconexion')  
    cantRegSincronizados = data.get('cantRegSincronizados')
    periodoDeCorte_str=data.get('periodoDeCorte')
    try:
      
        horarioDesconexion = datetime.strptime(horario_desconexion_str, '%Y-%m-%d %H:%M:%S')
        horarioReconexion = datetime.strptime(horario_reconexion_str, '%Y-%m-%d %H:%M:%S')

         # Convertir periodoDeCorte_str a timedelta
        periodoDeCorte_time = datetime.strptime(periodoDeCorte_str, '%H:%M:%S')
        periodoDeCorte = timedelta(hours=periodoDeCorte_time.hour, minutes=periodoDeCorte_time.minute, seconds=periodoDeCorte_time.second)

        result = notificarCorte(horarioDesconexion,horarioReconexion,cantRegSincronizados,periodoDeCorte)

        return jsonify(result), 200
    
    except Exception as e:
        mensaje_error = 'Error interno en el servidor: {}'.format(str(e))
        return jsonify({'error': mensaje_error}), 500

