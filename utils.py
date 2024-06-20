from datetime import datetime
import pytz
from dataclasses import dataclass
# horario = datetime.strptime(horario_str, '%Y-%m-%d %H:%M:%S')
# horario = datetime.strftime(horario, '%Y-%m-%d %H:%M:%S')
def utcToArgentina(dt: datetime):
  fecha_utc = datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, tzinfo=pytz.utc)
  zona_horaria_argentina = pytz.timezone('America/Argentina/Buenos_Aires')
  fecha_local = fecha_utc.astimezone(zona_horaria_argentina)
  return fecha_local

def getHoraMinutoFromHorario(horario: str): # "hh:mm"
  horario_splitted = horario.split(':')
  hora = int(horario_splitted[0])
  minuto = int(horario_splitted[1])

  return hora, minuto

    