import sqlite3
from tkinter import *
from tkinter import messagebox, ttk
from tkcalendar import Calendar
from datetime import datetime
import csv
import shutil
import os
import time
from datetime import datetime, timedelta
from tkinter import messagebox, simpledialog
import pandas as pd  # Librería necesaria para exportar a Excel
import webbrowser  # Para abrir WhatsApp Web

# Inicializar base de datos
def init_db():
    conn = sqlite3.connect("pacientes.db")
    cursor = conn.cursor()
    # Crear tablas si no existen
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            telefono TEXT,
            numero_tarjeta TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Medicaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER,
            medicacion TEXT NOT NULL,
            cn TEXT,
            fecha_inicio DATE NOT NULL,
            fecha_fin DATE NOT NULL,
            posologia INTEGER NOT NULL,
            unidades_por_caja INTEGER NOT NULL,
            FOREIGN KEY (paciente_id) REFERENCES Pacientes (id)
        )
    """)
    conn.commit()
    conn.close()

def añadir_paciente(root, calendar):
    def guardar_paciente():
        nombre = entry_nombre.get()
        apellidos = entry_apellidos.get()
        telefono = entry_telefono.get()
        numero_tarjeta = entry_tarjeta.get()

        if not nombre or not apellidos:
            messagebox.showwarning("Datos incompletos", "El nombre y los apellidos son obligatorios.")
            return

        # Conexión a la base de datos
        conn = sqlite3.connect("pacientes.db")
        cursor = conn.cursor()

        # Guardar el paciente
        cursor.execute("""
            INSERT INTO Pacientes (nombre, apellidos, telefono, numero_tarjeta)
            VALUES (?, ?, ?, ?)
        """, (nombre, apellidos, telefono, numero_tarjeta))
        paciente_id = cursor.lastrowid  # Obtener el ID del nuevo paciente

        # Guardar las medicaciones
        for medicacion in medicaciones:
            medicamento = medicacion["medicamento"]
            cn = medicacion.get("cn", "")
            fecha_inicio = medicacion["fecha_inicio"]
            fecha_fin = medicacion["fecha_fin"]
            posologia = medicacion["posologia"]
            unidades_por_caja = medicacion["unidades_por_caja"]

            # Insertar la medicación
            cursor.execute("""
                INSERT INTO Medicaciones (paciente_id, medicacion, cn, fecha_inicio, fecha_fin, posologia, unidades_por_caja)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (paciente_id, medicamento, cn, fecha_inicio, fecha_fin, posologia, unidades_por_caja))

            # Actualizar el calendario con las fechas de reabastecimiento
            marcar_dias_reabastecimiento(calendar, nombre, medicamento, fecha_inicio, fecha_fin, posologia, unidades_por_caja)

        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Paciente y medicaciones guardados correctamente.")
        ventana.destroy()

    def marcar_dias_reabastecimiento(calendar, nombre, medicamento, fecha_inicio, fecha_fin, posologia, unidades_por_caja):
        """Marca en el calendario las fechas de reabastecimiento con información del paciente y medicación."""
        fecha_actual = datetime.strptime(fecha_inicio, "%d-%m-%Y")
        fecha_final = datetime.strptime(fecha_fin, "%d-%m-%Y")
        
        # Calcular la frecuencia de reabastecimiento (días entre reposiciones)
        dias_cubiertos = unidades_por_caja // posologia  # Días que cubre una caja

        # Marcar solo el primer día
        evento = f"Paciente: {nombre}, Medicación: {medicamento}"
        calendar.calevent_create(fecha_actual, evento, "reposición")

        # Luego marcar los días de reabastecimiento, sumando la frecuencia cada vez
        while fecha_actual <= fecha_final:
            # Avanzar a la siguiente fecha de reposición
            fecha_actual += timedelta(days=dias_cubiertos)

            # Solo marcar si la fecha está dentro del rango (hasta fecha_final)
            if fecha_actual <= fecha_final:
                calendar.calevent_create(fecha_actual, evento, "reposición")

    def añadir_medicacion():
        def guardar_medicacion():
            medicamento = entry_medicamento.get()
            cn = entry_cn.get()
            fecha_inicio = calendar_inicio.get_date()
            fecha_fin = calendar_fin.get_date()
            try:
                posologia = int(entry_posologia.get())
                unidades_por_caja = int(entry_unidades.get())
            except ValueError:
                messagebox.showwarning("Datos inválidos", "Posología y unidades por caja deben ser números.")
                return

            if not medicamento or not fecha_inicio or not fecha_fin or posologia <= 0 or unidades_por_caja <= 0:
                messagebox.showwarning("Datos incompletos", "Debe ingresar todos los datos de la medicación.")
                return

            medicaciones.append({
                "medicamento": medicamento,
                "cn": cn,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "posologia": posologia,
                "unidades_por_caja": unidades_por_caja
            })
            lista_medicaciones.insert(
                END, f"{medicamento} (CN: {cn}) - {fecha_inicio} a {fecha_fin} ({posologia} tomas/día, {unidades_por_caja} unidades/caja)"
            )
            ventana_medicacion.destroy()

        # Ventana para añadir medicación
        ventana_medicacion = Toplevel()
        ventana_medicacion.title("Añadir Medicación")
        ventana_medicacion.geometry("800x600")
        ventana_medicacion.configure(bg="#50C878")

        Label(ventana_medicacion, text="Medicamento:", bg="#50C878").grid(row=0, column=0, padx=5, pady=5)
        entry_medicamento = Entry(ventana_medicacion)
        entry_medicamento.grid(row=0, column=1, padx=5, pady=5)

        Label(ventana_medicacion, text="CN (opcional):", bg="#50C878").grid(row=1, column=0, padx=5, pady=5)
        entry_cn = Entry(ventana_medicacion)
        entry_cn.grid(row=1, column=1, padx=5, pady=5)

        Label(ventana_medicacion, text="Fecha de inicio:", bg="#50C878").grid(row=2, column=0, padx=5, pady=5)
        calendar_inicio = Calendar(ventana_medicacion, selectmode="day", date_pattern="dd-mm-yyyy")
        calendar_inicio.grid(row=2, column=1, padx=5, pady=5)

        Label(ventana_medicacion, text="Fecha de fin:", bg="#50C878").grid(row=3, column=0, padx=5, pady=5)
        calendar_fin = Calendar(ventana_medicacion, selectmode="day", date_pattern="dd-mm-yyyy")
        calendar_fin.grid(row=3, column=1, padx=5, pady=5)

        Label(ventana_medicacion, text="Posología (tomas/día):", bg="#50C878").grid(row=4, column=0, padx=5, pady=5)
        entry_posologia = Entry(ventana_medicacion)
        entry_posologia.grid(row=4, column=1, padx=5, pady=5)

        Label(ventana_medicacion, text="Unidades por caja:", bg="#50C878").grid(row=5, column=0, padx=5, pady=5)
        entry_unidades = Entry(ventana_medicacion)
        entry_unidades.grid(row=5, column=1, padx=5, pady=5)

        Button(ventana_medicacion, text="Guardar Medicación", command=guardar_medicacion, bg="#007C5C", fg="white").grid(row=6, column=0, columnspan=2, pady=10)

    def eliminar_medicacion():
        seleccion = lista_medicaciones.curselection()
        if not seleccion:
            messagebox.showwarning("Seleccionar medicación", "Debe seleccionar una medicación para eliminar.")
            return
        del medicaciones[seleccion[0]]
        lista_medicaciones.delete(seleccion)

    # Crear ventana principal de añadir paciente
    ventana = Toplevel(root)
    ventana.title("Añadir Paciente")
    ventana.geometry("800x600")
    ventana.configure(bg="#50C878")

    medicaciones = []

    Label(ventana, text="Nombre:", bg="#50C878").grid(row=0, column=0, padx=5, pady=5)
    entry_nombre = Entry(ventana)
    entry_nombre.grid(row=0, column=1, padx=5, pady=5)

    Label(ventana, text="Apellidos:", bg="#50C878").grid(row=1, column=0, padx=5, pady=5)
    entry_apellidos = Entry(ventana)
    entry_apellidos.grid(row=1, column=1, padx=5, pady=5)

    Label(ventana, text="Teléfono:", bg="#50C878").grid(row=2, column=0, padx=5, pady=5)
    entry_telefono = Entry(ventana)
    entry_telefono.grid(row=2, column=1, padx=5, pady=5)

    Label(ventana, text="Número de Tarjeta:", bg="#50C878").grid(row=3, column=0, padx=5, pady=5)
    entry_tarjeta = Entry(ventana)
    entry_tarjeta.grid(row=3, column=1, padx=5, pady=5)

    Button(ventana, text="Añadir Medicación", command=añadir_medicacion, bg="#007C5C", fg="white").grid(row=4, column=0, columnspan=2, pady=10)

    lista_medicaciones = Listbox(ventana, height=10, width=50)
    lista_medicaciones.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

    Button(ventana, text="Eliminar Medicación", command=eliminar_medicacion, bg="#E74C3C", fg="white").grid(row=6, column=0, columnspan=2, pady=10)

    Button(ventana, text="Guardar Paciente", command=guardar_paciente, bg="#007C5C", fg="white").grid(row=7, column=0, columnspan=2, pady=10)

#Para marcar los dias de la medicacion en el calendario
from datetime import datetime, timedelta  # Asegurarse de importar correctamente

def marcar_dias_medicacion(calendar):
    # Eliminar eventos antiguos
    calendar.calevent_remove("reposición")
    calendar.calevent_remove("med")
    calendar.calevent_remove("ultimo_envase")

    conn = sqlite3.connect("pacientes.db")
    cursor = conn.cursor()

    # Obtener las fechas de inicio, fin, la posología diaria y las unidades por caja
    cursor.execute("""
        SELECT p.nombre, m.fecha_inicio, m.fecha_fin, m.posologia, m.unidades_por_caja, m.medicacion
        FROM Medicaciones m
        INNER JOIN Pacientes p ON p.id = m.paciente_id
    """)
    medicaciones = cursor.fetchall()
    conn.close()

    for medicacion in medicaciones:
        nombre_paciente, fecha_inicio, fecha_fin, posologia, unidades_por_caja, nombre_medicacion = medicacion
        try:
            inicio = datetime.strptime(fecha_inicio, "%d-%m-%Y")
            fin = datetime.strptime(fecha_fin, "%d-%m-%Y")

            # Calcular frecuencia de reposición (en días)
            frecuencia_dias = max(1, unidades_por_caja // posologia)

            actual = inicio
            while actual <= fin:
                # Primero, añadir el evento de Último Envase (verde) si estamos en el último mes
                if actual + timedelta(days=frecuencia_dias) > fin:
                    calendar.calevent_create(
                        actual,
                        f"Último Envase de {nombre_medicacion} - Paciente: {nombre_paciente}",
                        "ultimo_envase"
                    )
                else:
                    # De lo contrario, marcar como reposición normal (rojo)
                    calendar.calevent_create(
                        actual,
                        f"Reposición de {nombre_medicacion} - Paciente: {nombre_paciente}",
                        "med"
                    )
                actual += timedelta(days=frecuencia_dias)  # Avanzar a la próxima reposición
        except ValueError as e:
            print(f"Error al procesar fechas: {e}")  # Agrega un mensaje de depuración si ocurre un error

    # Configurar apariencia de los días
    calendar.tag_config("med", background="red", foreground="white")
    calendar.tag_config("ultimo_envase", background="green", foreground="white")

def ver_medicacion_dia(fecha, calendar):
    """Muestra la medicación programada para un día específico."""
    eventos = calendar.get_calevents(fecha)

    if not eventos:
        messagebox.showinfo("Sin eventos", "No hay medicación programada para este día.")
        return

    # Crear ventana emergente con la lista de medicaciones
    ventana_medicacion = Toplevel()
    ventana_medicacion.title(f"Medicaciones para {fecha}")
    ventana_medicacion.geometry("400x300")
    ventana_medicacion.configure(bg="#50C878")

    Label(ventana_medicacion, text=f"Medicaciones para el día {fecha}:", bg="#50C878", font=("Arial", 12, "bold")).pack(pady=10)

    for evento_id in eventos:
        evento_info = calendar.calevent_cget(evento_id, "text")
        Label(ventana_medicacion, text=evento_info, bg="#50C878").pack(pady=5)

        # Mostrar advertencia si es el último envase
        if "Último Envase" in evento_info:
            nombre_medicacion = evento_info.split("de")[1].strip()
            messagebox.showwarning(
                "⚠️ Último Envase ⚠️",
                f"ATENCIÓN: {evento_info}.\n\nAsegúrese de gestionar la medicación de este paciente."
            )

    Button(ventana_medicacion, text="Cerrar", command=ventana_medicacion.destroy, bg="#E74C3C", fg="white").pack(pady=10)

def agregar_medicacion():
    def guardar_medicacion():
        medicamento = entry_medicamento.get()
        cn = entry_cn.get()
        fecha_inicio = calendar_inicio.get_date()
        fecha_fin = calendar_fin.get_date()
        posologia = int(entry_posologia.get())
        unidades_por_caja = int(entry_unidades.get())

        if not medicamento or not fecha_inicio or not fecha_fin or posologia <= 0 or unidades_por_caja <= 0:
            messagebox.showwarning("Datos incompletos", "Todos los campos son obligatorios y deben ser válidos.")
            return

        medicaciones.append({
            "medicamento": medicamento,
            "cn": cn,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "posologia": posologia,
            "unidades_por_caja": unidades_por_caja
        })
        lista_medicaciones.insert(
            END, f"{medicamento} (CN: {cn}) - {fecha_inicio} a {fecha_fin} ({posologia} tomas/día)"
        )
        ventana_medicacion.destroy()

    ventana_medicacion = Toplevel()
    ventana_medicacion.title("Añadir Medicación")
    ventana_medicacion.geometry("800x600")
    ventana_medicacion.configure(bg="#50C878")

    Label(ventana_medicacion, text="Medicamento:", bg="#50C878").grid(row=0, column=0, padx=5, pady=5)
    entry_medicamento = Entry(ventana_medicacion)
    entry_medicamento.grid(row=0, column=1, padx=5, pady=5)

    Label(ventana_medicacion, text="CN (opcional):", bg="#50C878").grid(row=1, column=0, padx=5, pady=5)
    entry_cn = Entry(ventana_medicacion)
    entry_cn.grid(row=1, column=1, padx=5, pady=5)

    Label(ventana_medicacion, text="Fecha de inicio:", bg="#50C878").grid(row=2, column=0, padx=5, pady=5)
    calendar_inicio = Calendar(ventana_medicacion, selectmode="day", date_pattern="dd-mm-yyyy")
    calendar_inicio.grid(row=2, column=1, padx=5, pady=5)

    Label(ventana_medicacion, text="Fecha de fin:", bg="#50C878").grid(row=3, column=0, padx=5, pady=5)
    calendar_fin = Calendar(ventana_medicacion, selectmode="day", date_pattern="dd-mm-yyyy")
    calendar_fin.grid(row=3, column=1, padx=5, pady=5)

    Label(ventana_medicacion, text="Posología (tomas/día):", bg="#50C878").grid(row=4, column=0, padx=5, pady=5)
    entry_posologia = Entry(ventana_medicacion)
    entry_posologia.grid(row=4, column=1, padx=5, pady=5)

    Label(ventana_medicacion, text="Unidades por caja:", bg="#50C878").grid(row=5, column=0, padx=5, pady=5)
    entry_unidades = Entry(ventana_medicacion)
    entry_unidades.grid(row=5, column=1, padx=5, pady=5)

    Button(ventana_medicacion, text="Guardar Medicación", command=guardar_medicacion, bg="#007C5C", fg="white").grid(row=6, column=0, columnspan=2, pady=10)

# Función para mostrar la información del paciente seleccionado
def mostrar_pacientes():
    def seleccionar_paciente(event):
        seleccion = lista_pacientes.curselection()
        if seleccion:
            indice = seleccion[0]
            paciente_id = ids_pacientes[indice]
            mostrar_informacion_paciente(paciente_id)

    conn = sqlite3.connect("pacientes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, apellidos FROM Pacientes")
    pacientes = cursor.fetchall()
    conn.close()

    ventana_pacientes = Toplevel()
    ventana_pacientes.title("Lista de Pacientes")
    ventana_pacientes.configure(bg="#50C878")

    Label(ventana_pacientes, text="Pacientes:", bg="#50C878").pack(pady=5)

    lista_pacientes = Listbox(ventana_pacientes, width=50, height=20)
    lista_pacientes.pack(pady=5)

    ids_pacientes = []
    for paciente in pacientes:
        ids_pacientes.append(paciente[0])
        lista_pacientes.insert(END, f"{paciente[1]} {paciente[2]}")

    lista_pacientes.bind("<<ListboxSelect>>", seleccionar_paciente)

# Función para mostrar todos los pacientes
def ver_todos_pacientes():
    ventana_todos = Toplevel()
    ventana_todos.title("Todos los Pacientes")
    ventana_todos.geometry("800x600")
    ventana_todos.configure(bg="#50C878")  # Fondo verde

    # Frame para Treeview y Scrollbar
    frame = Frame(ventana_todos, bg="#50C878")
    frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    # Scrollbar vertical
    scrollbar_y = Scrollbar(frame, orient=VERTICAL)
    scrollbar_y.pack(side=RIGHT, fill=Y)

    # Scrollbar horizontal
    scrollbar_x = Scrollbar(frame, orient=HORIZONTAL)
    scrollbar_x.pack(side=BOTTOM, fill=X)

    # Treeview para mostrar pacientes y medicaciones
    tree = ttk.Treeview(
        frame,
        columns=("Nombre", "Apellidos", "Teléfono", "Medicación", "Fecha"),
        show="headings",
        yscrollcommand=scrollbar_y.set,
        xscrollcommand=scrollbar_x.set
    )
    tree.pack(fill=BOTH, expand=True)

    # Configuración de las columnas
    tree.heading("Nombre", text="Nombre")
    tree.heading("Apellidos", text="Apellidos")
    tree.heading("Teléfono", text="Teléfono")
    tree.heading("Medicación", text="Medicación")
    tree.heading("Fecha", text="Fecha")
    tree.column("Nombre", width=150)
    tree.column("Apellidos", width=150)
    tree.column("Teléfono", width=100)
    tree.column("Medicación", width=200)
    tree.column("Fecha", width=100)

    # Configuración del estilo verde para el Treeview
    style = ttk.Style()
    style.theme_use("default")
    style.configure(
        "Treeview",
        background="white",
        foreground="black",
        rowheight=25,
        fieldbackground="white"
    )
    style.map(
        "Treeview",
        background=[("selected", "#50C878")],  # Verde para selección
        foreground=[("selected", "white")]
    )

    # Vincular scrollbars con el Treeview
    scrollbar_y.config(command=tree.yview)
    scrollbar_x.config(command=tree.xview)

    # Obtener datos de la base de datos
    try:
        conn = sqlite3.connect("pacientes.db")
        cursor = conn.cursor()
        
        # Consulta para obtener los pacientes y sus medicaciones, ordenados por apellidos
        cursor.execute("""
            SELECT p.nombre, p.apellidos, p.telefono, m.medicacion, m.fecha_inicio
            FROM Pacientes p
            LEFT JOIN Medicaciones m ON p.id = m.paciente_id
            ORDER BY p.apellidos ASC
        """)
        datos = cursor.fetchall()
        conn.close()

        # Insertar los datos en el Treeview
        for fila in datos:
            tree.insert("", END, values=fila)

        # Evento para doble clic en un paciente
        def on_item_double_click(event):
            seleccion = tree.selection()
            if seleccion:
                item = tree.item(seleccion[0])
                nombre = item["values"][0]
                apellidos = item["values"][1]
                telefono = item["values"][2]
                medicacion = item["values"][3]
                fecha = item["values"][4]
                messagebox.showinfo(
                    "Información del Paciente",
                    f"Nombre: {nombre}\nApellidos: {apellidos}\nTeléfono: {telefono}\n"
                    f"Medicación: {medicacion}\nFecha de Inicio: {fecha}"
                )

        # Asociar el evento doble clic al Treeview
        tree.bind("<Double-1>", on_item_double_click)
    except sqlite3.Error as e:
        messagebox.showerror("Error de base de datos", str(e))

    # Botón para cerrar la ventana
    boton_cerrar = Button(
        ventana_todos,
        text="Cerrar",
        command=ventana_todos.destroy,
        bg="#007C5C",  # Verde oscuro
        fg="white"
    )
    boton_cerrar.pack(pady=10)


# Función para ver medicaciones del día
def ver_medicacion_dia(fecha_seleccionada):
    # Conexión a la base de datos
    conn = sqlite3.connect("pacientes.db")
    cursor = conn.cursor()

    # Convertir la fecha seleccionada al formato correcto
    fecha_seleccionada = datetime.strptime(fecha_seleccionada, "%d-%m-%Y").date()

    # Buscar medicaciones activas en esa fecha
    cursor.execute("""
        SELECT m.medicacion, m.fecha_inicio, m.fecha_fin, m.posologia, m.unidades_por_caja, p.nombre, p.apellidos
        FROM Medicaciones m
        JOIN Pacientes p ON m.paciente_id = p.id
    """)
    medicaciones = cursor.fetchall()
    conn.close()

    # Filtrar medicaciones que tienen reposición en el día seleccionado
    medicaciones_dia = []
    for medicacion in medicaciones:
        fecha_inicio = datetime.strptime(medicacion[1], "%d-%m-%Y").date()
        fecha_fin = datetime.strptime(medicacion[2], "%d-%m-%Y").date()
        posologia = medicacion[3]
        unidades_por_caja = medicacion[4]

        # Calcular frecuencia de reposición
        frecuencia_dias = max(1, unidades_por_caja // posologia)
        fecha_actual = fecha_inicio
        while fecha_actual <= fecha_fin:
            if fecha_actual == fecha_seleccionada:
                medicaciones_dia.append(medicacion)
                break
            fecha_actual += timedelta(days=frecuencia_dias)

    # Mostrar resultados
    if medicaciones_dia:
        mensaje = "\n".join([
            f"{medicacion[5]} {medicacion[6]} - Medicamento: {medicacion[0]} "
            f"({medicacion[3]} tomas/día, {medicacion[4]} unidades/caja)"
            for medicacion in medicaciones_dia
        ])
        messagebox.showinfo(f"Medicaciones para {fecha_seleccionada.strftime('%d-%m-%Y')}", mensaje)
    else:
        messagebox.showinfo("No hay medicación", "No hay medicación registrada para este día.")

def buscar_paciente_autocompletar(entry_busqueda, lista_sugerencias):
    def actualizar_lista():
        # Obtener texto del entry
        texto = entry_busqueda.get().strip().lower()
        lista_sugerencias.delete(0, END)

        # Si no hay texto, limpiar la lista y salir
        if not texto:
            return

        try:
            # Consultar la base de datos
            conn = sqlite3.connect("pacientes.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, nombre, apellidos
                FROM Pacientes
                WHERE LOWER(nombre || ' ' || apellidos) LIKE ?
            """, (f"%{texto}%",))
            resultados = cursor.fetchall()
            conn.close()

            # Si no hay resultados, mostrar mensaje en la lista
            if not resultados:
                lista_sugerencias.insert(END, "No se encontraron resultados")
                return

            # Añadir resultados a la lista de sugerencias
            for resultado in resultados:
                lista_sugerencias.insert(END, f"{resultado[1]} {resultado[2]} - ID: {resultado[0]}")

        except sqlite3.Error as e:
            messagebox.showerror("Error de base de datos", f"No se pudo realizar la búsqueda: {e}")

    def seleccionar_paciente(event):
        # Obtener la selección activa de la lista
        if lista_sugerencias.curselection():
            texto_seleccionado = lista_sugerencias.get(ACTIVE)
            if texto_seleccionado == "No se encontraron resultados":
                return  # No hacer nada si el texto seleccionado es el mensaje de "sin resultados"
            try:
                # Extraer el ID del texto seleccionado
                paciente_id = int(texto_seleccionado.split("- ID: ")[1])
                mostrar_informacion_paciente(paciente_id)
            except (IndexError, ValueError):
                messagebox.showerror("Error", "No se pudo obtener el ID del paciente.")

    # Vincular eventos
    lista_sugerencias.bind("<Double-1>", seleccionar_paciente)
    entry_busqueda.bind("<KeyRelease>", lambda _: actualizar_lista())

def mostrar_informacion_paciente(paciente_id):
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect("pacientes.db")
        cursor = conn.cursor()

        # Obtener los datos del paciente
        cursor.execute("SELECT * FROM Pacientes WHERE id = ?", (paciente_id,))
        paciente = cursor.fetchone()

        # Si el paciente no existe
        if not paciente:
            messagebox.showerror("Error", "El paciente no existe.")
            return

        # Obtener las medicaciones asociadas al paciente
        cursor.execute("""
            SELECT medicacion, cn, fecha_inicio, fecha_fin, posologia
            FROM Medicaciones
            WHERE paciente_id = ?
        """, (paciente_id,))
        medicaciones = cursor.fetchall()
        conn.close()

        # Crear ventana emergente
        ventana = Toplevel()
        ventana.title(f"Información de {paciente[1]} {paciente[2]}")
        ventana.configure(bg="#50C878")
        ventana.geometry("800x600")
        # Mostrar los datos del paciente
        Label(ventana, text=f"Nombre: {paciente[1]}", bg="#50C878").grid(row=0, column=0, padx=5, pady=5)
        Label(ventana, text=f"Apellidos: {paciente[2]}", bg="#50C878").grid(row=1, column=0, padx=5, pady=5)
        Label(ventana, text=f"Teléfono: {paciente[3]}", bg="#50C878").grid(row=2, column=0, padx=5, pady=5)
        Label(ventana, text=f"Tarjeta: {paciente[4]}", bg="#50C878").grid(row=3, column=0, padx=5, pady=5)

        # Mostrar la lista de medicaciones
        Label(ventana, text="Medicaciones:", bg="#50C878").grid(row=4, column=0, padx=5, pady=5)
        
        # Si el paciente tiene medicaciones, mostrarlas
        if medicaciones:
            for idx, medicacion in enumerate(medicaciones, start=5):
                texto = f"{medicacion[0]} (CN: {medicacion[1]}), {medicacion[2]} - {medicacion[3]} ({medicacion[4]} tomas/día)"
                Label(ventana, text=texto, bg="#50C878").grid(row=idx, column=0, padx=5, pady=5)
        else:
            # Si no tiene medicaciones, mostrar un mensaje informativo
            Label(ventana, text="Este paciente no tiene medicaciones registradas.", bg="#50C878").grid(row=5, column=0, padx=5, pady=5)

        # Botón para editar el paciente (siempre visible, independientemente de las medicaciones)
        Button(
            ventana, 
            text="Editar Paciente", 
            command=lambda: editar_paciente_desde_lista(ventana, paciente_id), 
            bg="#007C5C", 
            fg="white"
        ).grid(row=len(medicaciones) + 5, column=0, pady=10)

    except sqlite3.Error as e:
        messagebox.showerror("Error de base de datos", str(e))

def editar_paciente_desde_lista(root, paciente_id):
    def guardar_paciente():
        # Capturar datos actualizados del paciente
        nombre = entry_nombre.get()
        apellidos = entry_apellidos.get()
        telefono = entry_telefono.get()
        numero_tarjeta = entry_tarjeta.get()

        if not nombre or not apellidos:
            messagebox.showwarning("Datos incompletos", "El nombre y los apellidos son obligatorios.")
            return

        # Conexión a la base de datos
        conn = sqlite3.connect("pacientes.db")
        cursor = conn.cursor()

        # Actualizar datos del paciente
        cursor.execute("""
            UPDATE Pacientes
            SET nombre = ?, apellidos = ?, telefono = ?, numero_tarjeta = ?
            WHERE id = ?
        """, (nombre, apellidos, telefono, numero_tarjeta, paciente_id))

        # Eliminar medicaciones anteriores
        cursor.execute("DELETE FROM Medicaciones WHERE paciente_id = ?", (paciente_id,))

        # Guardar nuevas medicaciones
        for medicacion in medicaciones:
            cursor.execute("""
                INSERT INTO Medicaciones (paciente_id, medicacion, cn, fecha_inicio, fecha_fin, posologia, unidades_por_caja)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (paciente_id, medicacion["medicamento"], medicacion["cn"], medicacion["fecha_inicio"],
                  medicacion["fecha_fin"], medicacion["posologia"], medicacion["unidades_por_caja"]))

        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Paciente actualizado correctamente.")
        ventana.destroy()

    def eliminar_medicacion():
        seleccion = lista_medicaciones.curselection()
        if not seleccion:
            messagebox.showwarning("Seleccionar medicación", "Debe seleccionar una medicación para eliminar.")
            return

        # Eliminar de la lista en la interfaz
        medicaciones.pop(seleccion[0])
        lista_medicaciones.delete(seleccion[0])

        messagebox.showinfo("Éxito", "Medicamento eliminado correctamente.")

    def abrir_ventana_medicacion(accion, indice=None):
        """Ventana común para añadir o editar medicación."""
        def guardar():
            medicamento = entry_medicamento.get()
            cn = entry_cn.get()
            fecha_inicio = calendar_inicio.get_date()
            fecha_fin = calendar_fin.get_date()

            try:
                posologia = int(entry_posologia.get())
                unidades_por_caja = int(entry_unidades.get())
            except ValueError:
                messagebox.showwarning("Datos inválidos", "Posología y unidades por caja deben ser números.")
                return

            if not medicamento or not fecha_inicio or not fecha_fin or posologia <= 0 or unidades_por_caja <= 0:
                messagebox.showwarning("Datos incompletos", "Debe ingresar todos los datos de la medicación.")
                return

            nueva_medicacion = {
                "medicamento": medicamento,
                "cn": cn,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "posologia": posologia,
                "unidades_por_caja": unidades_por_caja,
            }

            if accion == "añadir":
                medicaciones.append(nueva_medicacion)
                lista_medicaciones.insert(
                    END, f"{medicamento} (CN: {cn}) - {fecha_inicio} a {fecha_fin} ({posologia} tomas/día, {unidades_por_caja} unidades/caja)"
                )
            elif accion == "editar" and indice is not None:
                medicaciones[indice] = nueva_medicacion
                lista_medicaciones.delete(indice)
                lista_medicaciones.insert(
                    indice, f"{medicamento} (CN: {cn}) - {fecha_inicio} a {fecha_fin} ({posologia} tomas/día, {unidades_por_caja} unidades/caja)"
                )

            messagebox.showinfo("Éxito", "Cambios guardados correctamente.")
            ventana_medicacion.destroy()

        # Configurar ventana
        ventana_medicacion = Toplevel()
        ventana_medicacion.title(f"{'Añadir' if accion == 'añadir' else 'Editar'} Medicación")
        ventana_medicacion.geometry("800x600")
        ventana_medicacion.configure(bg="#50C878")

        # Campos de entrada
        Label(ventana_medicacion, text="Medicamento:", bg="#50C878").grid(row=0, column=0, padx=5, pady=5)
        entry_medicamento = Entry(ventana_medicacion)
        entry_medicamento.grid(row=0, column=1, padx=5, pady=5)

        Label(ventana_medicacion, text="CN (opcional):", bg="#50C878").grid(row=1, column=0, padx=5, pady=5)
        entry_cn = Entry(ventana_medicacion)
        entry_cn.grid(row=1, column=1, padx=5, pady=5)

        # Configuración inicial del calendario
        fecha_inicio_dt = datetime.now()  # Fecha predeterminada si no se edita
        fecha_fin_dt = datetime.now()

        if accion == "editar" and indice is not None:
            medicacion = medicaciones[indice]
            entry_medicamento.insert(0, medicacion["medicamento"])
            entry_cn.insert(0, medicacion["cn"])
            # Convertir las fechas a datetime
            fecha_inicio_dt = datetime.strptime(medicacion["fecha_inicio"], "%d-%m-%Y")
            fecha_fin_dt = datetime.strptime(medicacion["fecha_fin"], "%d-%m-%Y")

        Label(ventana_medicacion, text="Fecha de inicio:", bg="#50C878").grid(row=2, column=0, padx=5, pady=5)
        calendar_inicio = Calendar(
            ventana_medicacion, selectmode="day", date_pattern="dd-mm-yyyy",
            year=fecha_inicio_dt.year, month=fecha_inicio_dt.month, day=fecha_inicio_dt.day
        )
        calendar_inicio.grid(row=2, column=1, padx=5, pady=5)

        Label(ventana_medicacion, text="Fecha de fin:", bg="#50C878").grid(row=3, column=0, padx=5, pady=5)
        calendar_fin = Calendar(
            ventana_medicacion, selectmode="day", date_pattern="dd-mm-yyyy",
            year=fecha_fin_dt.year, month=fecha_fin_dt.month, day=fecha_fin_dt.day
        )
        calendar_fin.grid(row=3, column=1, padx=5, pady=5)

        Label(ventana_medicacion, text="Posología (tomas/día):", bg="#50C878").grid(row=4, column=0, padx=5, pady=5)
        entry_posologia = Entry(ventana_medicacion)
        entry_posologia.grid(row=4, column=1, padx=5, pady=5)

        Label(ventana_medicacion, text="Unidades por caja:", bg="#50C878").grid(row=5, column=0, padx=5, pady=5)
        entry_unidades = Entry(ventana_medicacion)
        entry_unidades.grid(row=5, column=1, padx=5, pady=5)

        # Precargar otros datos si es una edición
        if accion == "editar" and indice is not None:
            entry_posologia.insert(0, medicacion["posologia"])
            entry_unidades.insert(0, medicacion["unidades_por_caja"])

        # Crear el botón de guardar
        Button(
            ventana_medicacion,
            text="Guardar",
            command=guardar,
            bg="#007C5C",
            fg="white"
        ).grid(row=6, column=0, columnspan=2, pady=10)
    # Obtener datos actuales del paciente
    conn = sqlite3.connect("pacientes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Pacientes WHERE id = ?", (paciente_id,))
    paciente = cursor.fetchone()

    cursor.execute("""
        SELECT medicacion, cn, fecha_inicio, fecha_fin, posologia, unidades_por_caja
        FROM Medicaciones
        WHERE paciente_id = ?
    """, (paciente_id,))
    medicaciones_db = cursor.fetchall()
    conn.close()

    # Crear ventana de edición
    ventana = Toplevel(root)
    ventana.title("Editar Paciente")
    ventana.geometry("800x600")
    ventana.configure(bg="#50C878")

    # Campos de texto para editar los datos del paciente
    Label(ventana, text="Nombre:", bg="#50C878").grid(row=0, column=0, padx=5, pady=5)
    entry_nombre = Entry(ventana)
    entry_nombre.insert(0, paciente[1])
    entry_nombre.grid(row=0, column=1, padx=5, pady=5)

    Label(ventana, text="Apellidos:", bg="#50C878").grid(row=1, column=0, padx=5, pady=5)
    entry_apellidos = Entry(ventana)
    entry_apellidos.insert(0, paciente[2])
    entry_apellidos.grid(row=1, column=1, padx=5, pady=5)

    Label(ventana, text="Teléfono:", bg="#50C878").grid(row=2, column=0, padx=5, pady=5)
    entry_telefono = Entry(ventana)
    entry_telefono.insert(0, paciente[3])
    entry_telefono.grid(row=2, column=1, padx=5, pady=5)

    Label(ventana, text="Número de Tarjeta:", bg="#50C878").grid(row=3, column=0, padx=5, pady=5)
    entry_tarjeta = Entry(ventana)
    entry_tarjeta.insert(0, paciente[4])
    entry_tarjeta.grid(row=3, column=1, padx=5, pady=5)

    # Crear lista para las medicaciones
    lista_medicaciones = Listbox(ventana, height=10, width=75)
    lista_medicaciones.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

    # Cargar medicaciones
    medicaciones = []
    for medicacion in medicaciones_db:
        lista_medicaciones.insert(
            END, 
            f"{medicacion[0]} (CN: {medicacion[1]}) - {medicacion[2]} a {medicacion[3]} ({medicacion[4]} tomas/día, {medicacion[5]} unidades/caja)"
        )
        medicaciones.append({
            "medicamento": medicacion[0],
            "cn": medicacion[1],
            "fecha_inicio": medicacion[2],
            "fecha_fin": medicacion[3],
            "posologia": medicacion[4],
            "unidades_por_caja": medicacion[5],
        })

    # Vincular doble clic en la lista de medicaciones
    lista_medicaciones.bind("<Double-1>", lambda event: abrir_ventana_medicacion("editar", lista_medicaciones.curselection()[0]))

    # Botones
    Button(
        ventana,
        text="Eliminar Medicación",
        command=eliminar_medicacion,
        bg="#E74C3C",
        fg="white"
    ).grid(row=6, column=1, padx=5, pady=10, sticky="e")

    Button(
        ventana,
        text="Añadir Medicación",
        command=lambda: abrir_ventana_medicacion("añadir"),
        bg="#007C5C",
        fg="white"
    ).grid(row=6, column=0, padx=5, pady=10, sticky="w")

    Button(
        ventana,
        text="Guardar Cambios",
        command=guardar_paciente,
        bg="#007C5C",
        fg="white"
    ).grid(row=7, column=0, columnspan=2, pady=10)



# Función para exportar datos a CSV
def exportar_datos():
    try:
        # Conexión a la base de datos
        conn = sqlite3.connect("pacientes.db")
        cursor = conn.cursor()

        # Obtener los datos de los pacientes
        cursor.execute("SELECT * FROM Pacientes")
        pacientes = cursor.fetchall()

        # Obtener los datos de las medicaciones
        cursor.execute("""
            SELECT p.nombre, p.apellidos, m.medicacion, m.cn, m.fecha_inicio, m.fecha_fin, m.posologia, m.unidades_por_caja
            FROM Medicaciones m
            INNER JOIN Pacientes p ON m.paciente_id = p.id
        """)
        medicaciones = cursor.fetchall()

        conn.close()

        if not pacientes and not medicaciones:
            messagebox.showwarning("Sin datos", "No hay datos para exportar.")
            return

        # Preguntar al usuario el formato de exportación
        formato = simpledialog.askstring(
            "Formato de Exportación",
            "¿A qué formato desea exportar los datos? (csv/excel)",
            initialvalue="excel"
        )

        if formato.lower() == "csv":
            # Exportar a CSV
            with open("pacientes_y_medicaciones.csv", "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)

                # Escribir encabezados para pacientes
                writer.writerow(["ID", "Nombre", "Apellidos", "Teléfono", "Número Tarjeta"])
                for paciente in pacientes:
                    writer.writerow(paciente)

                writer.writerow([])  # Línea vacía entre secciones

                # Escribir encabezados para medicaciones
                writer.writerow(["Paciente Nombre", "Paciente Apellidos", "Medicamento", "CN", "Fecha Inicio", "Fecha Fin", "Posología", "Unidades por Caja"])
                for medicacion in medicaciones:
                    writer.writerow(medicacion)

            messagebox.showinfo("Éxito", "Datos exportados correctamente a 'pacientes_y_medicaciones.csv'.")

        elif formato.lower() == "excel":
            # Exportar a Excel
            with pd.ExcelWriter("pacientes_y_medicaciones.xlsx") as writer:
                # Convertir datos de pacientes a un DataFrame y escribir en una hoja
                df_pacientes = pd.DataFrame(
                    pacientes,
                    columns=["ID", "Nombre", "Apellidos", "Teléfono", "Número Tarjeta"]
                )
                df_pacientes.to_excel(writer, sheet_name="Pacientes", index=False)

                # Convertir datos de medicaciones a un DataFrame y escribir en otra hoja
                df_medicaciones = pd.DataFrame(
                    medicaciones,
                    columns=["Paciente Nombre", "Paciente Apellidos", "Medicamento", "CN", "Fecha Inicio", "Fecha Fin", "Posología", "Unidades por Caja"]
                )
                df_medicaciones.to_excel(writer, sheet_name="Medicaciones", index=False)

            messagebox.showinfo("Éxito", "Datos exportados correctamente a 'pacientes_y_medicaciones.xlsx'.")

        else:
            messagebox.showwarning("Formato inválido", "Debe elegir 'csv' o 'excel'.")

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo exportar: {e}")

# Función para hacer backup de la base de datos
def backup_database():
    try:
        if not os.path.exists("pacientes.db"):
            messagebox.showerror("Error", "La base de datos 'pacientes.db' no existe.")
            return

        timestamp = time.strftime("%Y%m%d_%H%M%S")  # Formato legible para el timestamp
        backup_file = f"pacientes_backup_{timestamp}.db"

        shutil.copy("pacientes.db", backup_file)
        messagebox.showinfo("Backup realizado", f"Se ha creado un backup en '{backup_file}'.")

    except Exception as e:
        messagebox.showerror("Error", f"Error al crear el backup: {e}")



#Avisar por Whatsapp
def abrir_ventana_aviso_paciente():
    """Abre una ventana emergente para escribir un mensaje al paciente."""
    ventana_aviso = Toplevel()
    ventana_aviso.title("Avisar al Paciente")
    ventana_aviso.geometry("800x600")  # Tamaño actualizado
    ventana_aviso.configure(bg="#50C878")

    # Campo de búsqueda por nombre del paciente
    Label(ventana_aviso, text="Buscar paciente por nombre:", bg="#50C878").pack(pady=10)
    entry_nombre = Entry(ventana_aviso, width=30)
    entry_nombre.pack(pady=5)

    # Lista de sugerencias
    lista_sugerencias = Listbox(ventana_aviso, height=5, width=50)
    lista_sugerencias.pack(pady=5)

    def buscar_paciente(event=None):
        """Buscar el paciente por nombre y mostrar sugerencias en la lista."""
        texto = entry_nombre.get().strip().lower()
        lista_sugerencias.delete(0, "end")  # Limpiar la lista

        if not texto:
            return

        try:
            # Conectar a la base de datos y buscar pacientes que coincidan
            conn = sqlite3.connect("pacientes.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, nombre, apellidos, telefono
                FROM Pacientes
                WHERE LOWER(nombre || ' ' || apellidos) LIKE ?
            """, (f"%{texto}%",))
            resultados = cursor.fetchall()
            conn.close()

            if not resultados:
                lista_sugerencias.insert("end", "No se encontraron resultados.")
                return

            for resultado in resultados:
                lista_sugerencias.insert("end", f"{resultado[1]} {resultado[2]} - Tel: {resultado[3]} - ID: {resultado[0]}")

        except sqlite3.Error as e:
            messagebox.showerror("Error de base de datos", f"No se pudo realizar la búsqueda: {e}")

    entry_nombre.bind("<KeyRelease>", buscar_paciente)

    # Seleccionar paciente de la lista
    def seleccionar_paciente(event):
        """Seleccionar un paciente de la lista y completar el teléfono en el campo correspondiente."""
        seleccion = lista_sugerencias.curselection()
        if seleccion:
            texto_seleccionado = lista_sugerencias.get(seleccion[0])
            paciente_id = int(texto_seleccionado.split("ID: ")[1])  # Extraer ID de la selección
            # Buscar el teléfono del paciente seleccionado
            try:
                conn = sqlite3.connect("pacientes.db")
                cursor = conn.cursor()
                cursor.execute("SELECT telefono FROM Pacientes WHERE id = ?", (paciente_id,))
                telefono = cursor.fetchone()[0]
                conn.close()

                entry_telefono.delete(0, "end")  # Limpiar el campo
                entry_telefono.insert(0, telefono)  # Completar con el número de teléfono
            except sqlite3.Error as e:
                messagebox.showerror("Error de base de datos", f"No se pudo obtener el teléfono: {e}")

    lista_sugerencias.bind("<Double-1>", seleccionar_paciente)

    # Campo para el teléfono
    Label(ventana_aviso, text="Número de teléfono del paciente:", bg="#50C878").pack(pady=10)
    entry_telefono = Entry(ventana_aviso, width=30)
    entry_telefono.pack(pady=5)

    # Campo de texto para escribir el mensaje
    Label(ventana_aviso, text="Escribir mensaje:", bg="#50C878").pack(pady=10)
    text_mensaje = Text(ventana_aviso, width=50, height=10)
    text_mensaje.pack(pady=5)

    # Scrollbar para el campo de texto
    scrollbar = Scrollbar(ventana_aviso, orient="vertical", command=text_mensaje.yview)
    scrollbar.pack(side="right", fill="y")
    text_mensaje.config(yscrollcommand=scrollbar.set)

    # Botón para enviar el mensaje
    def enviar_whatsapp():
        telefono = entry_telefono.get().strip()
        mensaje = text_mensaje.get("1.0", "end").strip()

        if not telefono:
            messagebox.showwarning("Error", "El número de teléfono es obligatorio.")
            return
        if not mensaje:
            messagebox.showwarning("Error", "El mensaje no puede estar vacío.")
            return

        # Formatear el enlace para WhatsApp Web
        enlace_whatsapp = f"https://wa.me/{telefono}?text={mensaje.replace(' ', '%20')}"
        webbrowser.open(enlace_whatsapp)
        ventana_aviso.destroy()

    Button(ventana_aviso, text="Enviar Mensaje por WhatsApp", command=enviar_whatsapp, bg="#007C5C", fg="white").pack(pady=10)
# Configuración principal
def main():
    # Configuración inicial
    root = Tk()
    root.title("Gestión de Medicaciones")
    root.configure(bg="#50C878")
    root.geometry("800x600")  # Aumentar el tamaño de la ventana

    # Calendario
    calendar = Calendar(root, selectmode="day", date_pattern="dd-mm-yyyy", background="#50C878", foreground="white")
    calendar.pack(pady=10)
    marcar_dias_medicacion(calendar)
    calendar.bind("<<CalendarSelected>>", lambda event: ver_medicacion_dia(calendar.get_date()))

    # Botones principales
    Button(root, text="Añadir Paciente", command=lambda: añadir_paciente(root, calendar), bg="#007C5C", fg="white").pack(pady=5)
    Button(root, text="Ver Todos los Pacientes", command=ver_todos_pacientes, bg="#007C5C", fg="white").pack(pady=5)
    Button(root, text="Exportar a CSV o Excel", command=exportar_datos, bg="#007C5C", fg="white").pack(pady=5)
    Button(root, text="Copia de Seguridad", command=backup_database, bg="#007C5C", fg="white").pack(pady=5)
    Button(root, text="Avisar al Paciente por Whatsapp", command=abrir_ventana_aviso_paciente, bg="#007C5C", fg="white").pack(pady=5)

    # Búsqueda de pacientes
    frame_busqueda = Frame(root, bg="#50C878")
    frame_busqueda.pack(pady=10)

    # Etiqueta para la búsqueda
    Label(frame_busqueda, text="Búsqueda de Pacientes:", bg="#50C878", fg="white").pack(side=LEFT, padx=5)

    # Entrada de búsqueda
    entry_busqueda = Entry(frame_busqueda)
    entry_busqueda.pack(side=LEFT, padx=5)

    # Botón de limpiar búsqueda
    Button(frame_busqueda, text="Limpiar", 
           command=lambda: (entry_busqueda.delete(0, END), lista_sugerencias.delete(0, END)),
           bg="#E74C3C", fg="white").pack(side=LEFT, padx=5)

    # Lista de sugerencias con scroll
    frame_lista = Frame(root)
    frame_lista.pack(pady=5)

    lista_sugerencias = Listbox(frame_lista, height=10, width=50)
    lista_sugerencias.pack(side=LEFT, padx=5)

    scrollbar = Scrollbar(frame_lista, orient=VERTICAL, command=lista_sugerencias.yview)
    scrollbar.pack(side=LEFT, fill=Y)
    lista_sugerencias.config(yscrollcommand=scrollbar.set)

    # Eventos para la búsqueda
    entry_busqueda.bind("<KeyRelease>", lambda event: buscar_paciente_autocompletar(entry_busqueda, lista_sugerencias))
    entry_busqueda.bind("<Return>", lambda event: buscar_paciente_autocompletar(entry_busqueda, lista_sugerencias))
    lista_sugerencias.bind("<Double-1>", lambda event: mostrar_informacion_paciente(int(lista_sugerencias.get(ACTIVE).split("- ID: ")[1])))

    # Copyright en la parte inferior derecha
    copyright_label = Label(root, text="© PharmaJava", bg="#50C878", fg="white")
    copyright_label.pack(side="bottom", anchor="e", padx=10, pady=10)

    root.mainloop()

# Inicializar base de datos y lanzar programa
if __name__ == "__main__":
    init_db()
    main()
