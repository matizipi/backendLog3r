import subprocess
import sys

def launch_script():
    # Lanza el script salidaAutomatica.py en segundo plano
    process = subprocess.Popen(
        ["python", "salidaAutomatica.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True  # Asegura que las salidas sean cadenas de texto
    )

    # Lee las salidas de stdout y stderr
    for line in process.stdout:
        print("STDOUT:", line, end='')

    for line in process.stderr:
        print("STDERR:", line, end='')

if __name__ == "__main__":
    print("Inicio de launch_script_segundo_plano.py")
    launch_script()
    print("Script salidaAutomatica.py ejecutándose en segundo plano.")