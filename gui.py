# gui.py
import tkinter as tk
from tkinter import ttk, messagebox
import threading

def lanzar_gui(callback_iniciar):
    ventana = tk.Tk()
    ventana.title("Auditoría SSH / Telnet")
    ventana.geometry("700x500")

    pagina_actual = [0]
    resultados = []

    # Actualiza tabla y contador con datos actuales
    def actualizar_tabla():
        tabla.delete(*tabla.get_children())
        inicio = pagina_actual[0] * 15
        fin = inicio + 15
        for dato in resultados[inicio:fin]:
            tabla.insert("", "end", values=(dato['ip'], dato['servicio'], dato['puerto'], dato['pais']))
        label_total.config(text=f"Total IPs encontradas: {len(resultados)}")

    def siguiente():
        if (pagina_actual[0] + 1) * 15 < len(resultados):
            pagina_actual[0] += 1
            actualizar_tabla()

    def anterior():
        if pagina_actual[0] > 0:
            pagina_actual[0] -= 1
            actualizar_tabla()

    # Proceso ejecutado en un hilo separado
    def hilo_auditoria():
        encontrados, exitosos = callback_iniciar(on_nueva_ip)
        boton_iniciar.config(state="normal")
        messagebox.showinfo("Auditoría completada", f"Se encontraron {len(encontrados)} IPs.\nAccesos exitosos: {len(exitosos)}")

    # Cada vez que se detecta una IP, se agrega y actualiza interfaz
    def on_nueva_ip(nueva_ip):
        resultados.append(nueva_ip)
        actualizar_tabla()

    def iniciar_auditoria():
        resultados.clear()
        actualizar_tabla()
        boton_iniciar.config(state="disabled")
        threading.Thread(target=hilo_auditoria, daemon=True).start()

    # UI básica
    texto = tk.Label(ventana, text="Esta herramienta es solo para fines educativos.\nEl uso indebido puede tener consecuencias legales.", fg="red")
    texto.pack(pady=10)

    check_var = tk.BooleanVar()
    def on_check():
        if check_var.get():
            checkbox.config(state="disabled")
            boton_iniciar.config(state="normal")

    checkbox = tk.Checkbutton(ventana, text="Acepto los términos y condiciones", variable=check_var, command=on_check)
    checkbox.pack()

    boton_iniciar = tk.Button(ventana, text="Iniciar Auditoría", state="disabled", command=iniciar_auditoria)
    boton_iniciar.pack(pady=5)

    label_total = tk.Label(ventana, text="Total IPs encontradas: 0")
    label_total.pack()

    columnas = ("IP", "Servicio", "Puerto", "País")
    tabla = ttk.Treeview(ventana, columns=columnas, show="headings", height=15)
    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, width=150)
    tabla.pack(pady=5)

    frame_botones = tk.Frame(ventana)
    frame_botones.pack()
    tk.Button(frame_botones, text="Anterior", command=anterior).grid(row=0, column=0, padx=10)
    tk.Button(frame_botones, text="Siguiente", command=siguiente).grid(row=0, column=1, padx=10)

    ventana.mainloop()
