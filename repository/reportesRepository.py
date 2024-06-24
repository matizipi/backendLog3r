import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from database.connection import db


def notificarInfoDeSincronizacion(horarioDesconexion,horarioReconexion,cantRegSincronizados,periodoDeCorte,incompatibles):
    asunto="Notificación sobre corte de Internet (Log3rApp)"
    personal_jerarquico =  obtener_usuarios_por_rol("personal jerárquico")

    emails = [user['email'] for user in personal_jerarquico]

    mensaje=generar_cuerpo_notificacion(horarioDesconexion,horarioReconexion,cantRegSincronizados,periodoDeCorte,incompatibles)

    for email in emails:
        send_email(email, asunto, mensaje)

def generar_cuerpo_notificacion(horarioDesconexion,horarioReconexion,cantRegSincronizados,periodoDeCorte,incompatibles):
    cuerpoCorte = (
        f"Se ha detectado un corte de Internet en la aplicación:\n\n"
        f"Horario de Desconexión: {horarioDesconexion}\n"
        f"Horario de Reconexión: {horarioReconexion}\n"
        f"Cantidad de Registros Sincronizados: {cantRegSincronizados}\n\n"
        f"Tiempo total sin conexión de internet: {periodoDeCorte} (horas\\minutos\\segundos) \n\n"        
    )
    print(f'cantidad de incompatibles:{len(incompatibles)}')

    if len(incompatibles) > 0:
        cuerpoNotificacion = cuerpoCorte + generar_cuerpo_notificacion_incompatibilidad(incompatibles)
    else:
        cuerpoNotificacion = cuerpoCorte + "Log3rApp by AlphaTeam"
  
    return cuerpoNotificacion

def generar_cuerpo_notificacion_incompatibilidad(registros):
    cuerpo = "Se ha detectado una incompatibilidad con los siguientes registros offline: (No son Usuarios registrados)\n\n"
    
    for registro in registros:
        dni = registro.get('dni')
        nombre = registro.get('nombre')
        apellido = registro.get('apellido')
        cuerpo += (
            f"Usuario: {nombre} {apellido}\n"
            f"DNI: {dni}\n\n"
        )
    
    cuerpo += "Log3rApp by AlphaTeam"
    return cuerpo
   

def notificarCambioDeTitularidad(nombre,apellido,json_usuario_original,json_usuario_modificado):
    asunto="Notificación sobre cambio de titularidad"
    personal_jerarquico =  obtener_usuarios_por_rol("personal jerárquico")
    emails = [user['email'] for user in personal_jerarquico]
    mensaje=generar_cuerpo_cambio_titularidad(nombre, apellido, json_usuario_original,json_usuario_modificado)
    for email in emails:
        send_email(email, asunto, mensaje)

def generar_cuerpo_cambio_titularidad(nombre, apellido, original, modificado):
    cambios = []
    for key in original:
        if key in modificado and original[key] != modificado[key]:
            cambios.append(f"{key}: {original[key]} -> {modificado[key]}")
    
    if not cambios:
        return "No se han realizado modificaciones."
    
    cuerpo = f"Se han realizado los siguientes cambios en la información del usuario:\n\n{nombre} {apellido}\n"
    cuerpo += "\n".join(cambios)
    return cuerpo


def send_email(to_email, subject, message):

    smtp_server = 'smtp.office365.com'
    smtp_port = 587
    smtp_user = os.getenv('OUTLOOK_USER') 
    smtp_password = os.getenv('OUTLOOK_PASSWORD') 
    
    # Configuración del mensaje
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject

    # Adjuntar el cuerpo del mensaje
    msg.attach(MIMEText(message, 'plain'))

    # Conectar al servidor SMTP y enviar el correo
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, to_email, msg.as_string())
        server.quit()
        print(f'Correo enviado a {to_email}')
    except Exception as e:
        print(f'Error al enviar el correo a {to_email}: {e}')

##Metodo hecho por imposibilidad de importar debido a importación circular        

def obtener_usuarios_por_rol(role_name):
    collection = db['usuarios']
    results = collection.find({ "rol": role_name })
    users = []
    for user in results:
        user['_id'] = str(user['_id'])
        try:
            for i in range(len(user['horarios'])):
                user['horarios'][i]['_id'] = str(user['horarios'][i]['_id'])
        except Exception as e:
            pass # borrar try-except cuando todos los usuarios de la db tengan el campo "horarios"
        users.append(user)

    return users 
