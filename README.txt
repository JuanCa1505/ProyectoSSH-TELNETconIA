==============================================
 PROYECTO: Auditoría SSH / Telnet con Shodan
==============================================

Autor: Juan Camilo Ospina
Curso: Seguridad Informática

-------------------------------------------
	   DESCRIPCIÓN GENERAL
-------------------------------------------

Esta herramienta permite realizar una auditoría automatizada de servicios SSH y Telnet expuestos en internet, específicamente en los países de Colombia y Argentina. Utiliza la API de Shodan para identificar dispositivos con estos servicios activos, y luego intenta autenticarse mediante pruebas de credenciales comunes.

El objetivo es evidenciar posibles configuraciones inseguras en servicios de administración remota (SSH/Telnet), con fines exclusivamente educativos y de pruebas éticas.

-------------------------------------------
	  FUNCIONALIDADES PRINCIPALES
-------------------------------------------

✔ Búsqueda de servicios SSH y Telnet en Shodan por país.
✔ Detección de puertos abiertos (no solo los predeterminados).
✔ Validación masiva y automatizada de credenciales (SSH con paramiko, Telnet con pexpect).
✔ Interfaz gráfica con tabla, paginación y feedback en tiempo real.
✔ Modo CLI alternativo sin GUI.
✔ Registro de accesos exitosos (IPs, credenciales, país).
✔ Log de errores y eventos amigable (errores.log).

-------------------------------------------
 	   ESTRUCTURA DE ARCHIVOS
-------------------------------------------

- main.py              → Lógica principal, escaneo y validación.
- gui.py               → Interfaz gráfica Tkinter.
- config.py            → Configuración: API key, países, servicios, etc.
- credentials.txt      → Lista de combinaciones usuario:contraseña.
- Acceso_exitoso.txt   → Resultados con IPs y credenciales exitosas.
- errores.log          → Log de errores y eventos importantes.
- requerimientosPrevios.txt → Lista de dependencias.

-------------------------------------------
	    USO DE LA HERRAMIENTA
-------------------------------------------

▶ GUI (recomendado):
$ python3 main.py

▶ Modo CLI:
$ python3 main.py --cli

▶ Crear entorno virtual:
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requerimientosPrevios.txt

-------------------------------------------
	 EJEMPLO DE credentials.txt
-------------------------------------------

admin:admin
root:toor
admin:123456
user:user
admin:password
...

Puedes personalizar este archivo para realizar pruebas sobre diferentes dispositivos.

-------------------------------------------
      ALCANCE Y LIMITACIONES TÉCNICAS
-------------------------------------------

Alcance:
- Herramienta educativa para análisis de exposición de servicios.
- Compatible con Python 3.11+ y sistemas Linux.
- Uso de API Shodan con límite configurable.

Limitaciones:
- Requiere API key válida de Shodan.
- No detecta dispositivos ocultos tras firewalls/NAT.
- Algunas conexiones Telnet pueden necesitar ajustes según el banner.
- No implementa fuerza bruta, solo validación con lista predefinida.

-------------------------------------------
	        USO ÉTICO Y LEGAL
-------------------------------------------

Esta herramienta ha sido desarrollada únicamente con fines educativos. El uso no autorizado o contra sistemas ajenos sin permiso expreso constituye una actividad ilegal y viola códigos éticos de ciberseguridad.

El autor NO se hace responsable por un mal uso del programa.

===========================================
