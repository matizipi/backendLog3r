from flask import Blueprint, request, jsonify
from repository.horariosRepository import get_horarios_repository, get_horario_repository, post_horarios_repository, put_horarios_repository, delete_horarios_repository

horarios_bp = Blueprint('horarios', __name__)

@horarios_bp.route('/', methods=['GET'])
def get_horarios():
    horarios = get_horarios_repository()
    return jsonify(horarios)


@horarios_bp.route('/<horario_id>', methods=['GET'])
def get_horario(horario_id):
    role = get_horario_repository(horario_id)
    return jsonify(role), 200 if role is not None else 404


@horarios_bp.route('/', methods=['POST'])
def post_horario():
    data = request.json
    horario_entrada = data.get('horarioEntrada')
    horario_salida = data.get('horarioSalida')
    tipo = data.get('tipo')

    try:
      validateHorarios(horario_entrada, horario_salida, tipo)
    except Exception as e:
      return jsonify({'message':e.args[0]}), 400

    try:
      new_role = post_horarios_repository(horario_entrada, horario_salida, tipo)
      return jsonify(new_role), 201
    except Exception as e:
      return jsonify({'message':e.args[0]}), 500


@horarios_bp.route('/<_id>', methods=['PUT'])
def put_horario(_id):
    data = request.json

    horario_entrada = data.get('horarioEntrada')
    horario_salida = data.get('horarioSalida')
    tipo = data.get('tipo')
    try:
      validateHorarios(horario_entrada, horario_salida, tipo)
    except Exception as e:
      return jsonify({'message':e.args[0]}), 400

    try:
      updateResult = put_horarios_repository(_id, horario_entrada, horario_salida, tipo)
      return jsonify(updateResult)
    except Exception as e:
      return jsonify({'message':e.args[0]}), 500


@horarios_bp.route('/<_id>', methods=['DELETE'])
def delete_horario(_id):
    try:
      deleteResult = delete_horarios_repository(_id)
      return jsonify(deleteResult)
    except Exception as e:
      return jsonify({'message':e.args[0]}), 500


def validateHorarios(horario_entrada: str, horario_salida: str, tipo: str):
    if len(horario_entrada) != 5 or len(horario_entrada) != 5:
        raise RuntimeError('Los horarios deben ser en formato hh:mm')
    
    horario_entrada_splitted = horario_entrada.split(':')
    horario_salida_splitted = horario_salida.split(':')
    if len(horario_entrada_splitted) != 2 or len(horario_salida_splitted) != 2:
        raise RuntimeError('Los horarios deben ser en formato hh:mm')
    
    hora_entrada = int(horario_entrada_splitted[0])
    minuto_entrada = int(horario_entrada_splitted[1])

    hora_salida = int(horario_salida_splitted[0])
    minuto_salida = int(horario_salida_splitted[1])

    if not (0 <= hora_entrada <= 23) or not (0 <= hora_salida <= 23):
      raise RuntimeError('Horas inválidas')

    if not (0 <= minuto_entrada <= 59) or not (0 <= minuto_salida <= 59):
      raise RuntimeError('Minutos inválidos')
        
    if hora_salida < hora_entrada or (hora_entrada == hora_salida and minuto_salida <= minuto_entrada):
        raise RuntimeError('El horario de entrada debe ser menor al de salida')
    
    tipos = ['lunes a viernes', 'sabado']
    if tipo not in tipos:
      raise RuntimeError('Tipo inválido. Posibles valores: {}'.format(tipos))