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
    """
    Inicializa la base de datos y crea las tablas necesarias si no existen.
    Incluye la columna 'ultima_actualizacion' directamente en la definición de la tabla Medicaciones.
    """
    # Conexión a la base de datos
    conn = sqlite3.connect("pacientes.db")
    cursor = conn.cursor()

    # Crear tabla Pacientes si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            telefono TEXT,
            numero_tarjeta TEXT
        )
    """)

    # Crear tabla Medicaciones con la columna 'ultima_actualizacion'
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
            ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
                INSERT INTO Medicaciones (
                    paciente_id, medicacion, cn, fecha_inicio, fecha_fin, posologia, unidades_por_caja, ultima_actualizacion
                ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
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
        ventana_medicacion.geometry("1024x7680")
        ventana_medicacion.configure(bg="#50C878")

        Label(ventana_medicacion, text="Medicamento:", bg="#50C878", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10)
        entry_medicamento = Entry(ventana_medicacion, font=("Arial", 12))
        entry_medicamento.grid(row=0, column=1, padx=10, pady=10)

        Label(ventana_medicacion, text="CN (opcional):", bg="#50C878", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10)
        entry_cn = Entry(ventana_medicacion, font=("Arial", 12))
        entry_cn.grid(row=1, column=1, padx=10, pady=10)

        Label(ventana_medicacion, text="Fecha de inicio:", bg="#50C878", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=10)
        calendar_inicio = Calendar(ventana_medicacion, selectmode="day", date_pattern="dd-mm-yyyy", locale="es_ES", font=("Arial", 12))
        calendar_inicio.grid(row=2, column=1, padx=10, pady=10)

        Label(ventana_medicacion, text="Fecha de fin:", bg="#50C878", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=10)
        calendar_fin = Calendar(ventana_medicacion, selectmode="day", date_pattern="dd-mm-yyyy", locale="es_ES", font=("Arial", 12))
        calendar_fin.grid(row=3, column=1, padx=10, pady=10)

        Label(ventana_medicacion, text="Posología (tomas/día):", bg="#50C878", font=("Arial", 12)).grid(row=4, column=0, padx=10, pady=10)
        entry_posologia = Entry(ventana_medicacion, font=("Arial", 12))
        entry_posologia.grid(row=4, column=1, padx=10, pady=10)

        Label(ventana_medicacion, text="Unidades por caja:", bg="#50C878", font=("Arial", 12)).grid(row=5, column=0, padx=10, pady=10)
        entry_unidades = Entry(ventana_medicacion, font=("Arial", 12))
        entry_unidades.grid(row=5, column=1, padx=10, pady=10)

        Button(ventana_medicacion, text="Guardar Medicación", command=guardar_medicacion, bg="#007C5C", fg="white", font=("Arial", 12)).grid(row=6, column=0, columnspan=2, pady=20)

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

    # Campos de entrada con etiquetas y un diseño bonito
    Label(ventana, text="Nombre:", bg="#50C878", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10)
    entry_nombre = Entry(ventana, font=("Arial", 12))
    entry_nombre.grid(row=0, column=1, padx=10, pady=10)

    Label(ventana, text="Apellidos:", bg="#50C878", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10)
    entry_apellidos = Entry(ventana, font=("Arial", 12))
    entry_apellidos.grid(row=1, column=1, padx=10, pady=10)

    Label(ventana, text="Teléfono:", bg="#50C878", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=10)
    entry_telefono = Entry(ventana, font=("Arial", 12))
    entry_telefono.grid(row=2, column=1, padx=10, pady=10)

    Label(ventana, text="Número de Tarjeta:", bg="#50C878", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=10)
    entry_tarjeta = Entry(ventana, font=("Arial", 12))
    entry_tarjeta.grid(row=3, column=1, padx=10, pady=10)

    Button(ventana, text="Añadir Medicación", command=añadir_medicacion, bg="#007C5C", fg="white", font=("Arial", 12)).grid(row=4, column=0, columnspan=2, pady=10)

    lista_medicaciones = Listbox(ventana, height=10, width=50, font=("Arial", 12))
    lista_medicaciones.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    Button(ventana, text="Eliminar Medicación", command=eliminar_medicacion, bg="#E74C3C", fg="white", font=("Arial", 12)).grid(row=6, column=0, columnspan=2, pady=10)

    Button(ventana, text="Guardar Paciente", command=guardar_paciente, bg="#007C5C", fg="white", font=("Arial", 12)).grid(row=7, column=0, columnspan=2, pady=20)

#Para marcar los dias de la medicacion en el calendario
from datetime import datetime, timedelta  # Asegurarse de importar correctamente


def marcar_dias_medicacion(calendar, ultima_actualizacion=None):
    """
    Marca en el calendario las fechas de reposición (rojo) y último envase (verde).
    Al hacer clic en un día:
      1. Muestra notificación de "Último Envase" si existe.
      2. Luego, muestra notificaciones con otras medicaciones para esa fecha.
    :param calendar: Widget de calendario.
    :param ultima_actualizacion: Timestamp de la última actualización conocida.
    """
    # Eliminar eventos antiguos
    calendar.calevent_remove("reposición")
    calendar.calevent_remove("ultimo_envase")

    conn = sqlite3.connect("pacientes.db")
    cursor = conn.cursor()

    # Consultar medicaciones actualizadas después de la última modificación, si aplica
    if ultima_actualizacion:
        query = """
            SELECT p.nombre, m.fecha_inicio, m.fecha_fin, m.posologia, m.unidades_por_caja, m.medicacion, m.ultima_actualizacion
            FROM Medicaciones m
            INNER JOIN Pacientes p ON p.id = m.paciente_id
            WHERE m.ultima_actualizacion > ?
        """
        cursor.execute(query, (ultima_actualizacion,))
    else:
        query = """
            SELECT p.nombre, m.fecha_inicio, m.fecha_fin, m.posologia, m.unidades_por_caja, m.medicacion, m.ultima_actualizacion
            FROM Medicaciones m
            INNER JOIN Pacientes p ON p.id = m.paciente_id
        """
        cursor.execute(query)

    medicaciones = cursor.fetchall()
    conn.close()

    # Marcar eventos en el calendario
    nueva_ultima_actualizacion = ultima_actualizacion
    for medicacion in medicaciones:
        nombre_paciente, fecha_inicio, fecha_fin, posologia, unidades_por_caja, nombre_medicacion, ultima_actualizacion_db = medicacion

        # Actualizar la última modificación conocida
        if not nueva_ultima_actualizacion or ultima_actualizacion_db > nueva_ultima_actualizacion:
            nueva_ultima_actualizacion = ultima_actualizacion_db

        # Parsear fechas
        inicio = datetime.strptime(fecha_inicio, "%d-%m-%Y")
        fin = datetime.strptime(fecha_fin, "%d-%m-%Y")

        # Calcular frecuencia de reposición (en días)
        frecuencia_dias = max(1, unidades_por_caja // posologia)

        # Añadir eventos al calendario
        actual = inicio
        while actual <= fin:
            if actual + timedelta(days=frecuencia_dias) > fin:  # Último envase
                calendar.calevent_create(
                    actual,
                    f"Último Envase de {nombre_medicacion} - Paciente: {nombre_paciente}",
                    "ultimo_envase"
                )
            else:  # Reposición normal
                calendar.calevent_create(
                    actual,
                    f"Reposición de {nombre_medicacion} - Paciente: {nombre_paciente}",
                    "reposición"
                )
            actual += timedelta(days=frecuencia_dias)

    # Configurar colores de los eventos
    calendar.tag_config("reposición", background="red", foreground="white")
    calendar.tag_config("ultimo_envase", background="green", foreground="white")

    # Vincular el evento de clic para mostrar notificaciones
    def mostrar_notificacion_evento(event):
        fecha_seleccionada = calendar.get_date()
        eventos = calendar.get_calevents(datetime.strptime(fecha_seleccionada, "%d-%m-%Y"))

        # Inicializar listas para separar eventos
        eventos_ultimo_envase = []
        eventos_reposicion = []

        for evento_id in eventos:
            evento_info = calendar.calevent_cget(evento_id, "text")
            evento_tags = calendar.calevent_cget(evento_id, "tags")

            if "ultimo_envase" in evento_tags:
                eventos_ultimo_envase.append(evento_info)
            elif "reposición" in evento_tags:
                eventos_reposicion.append(evento_info)

        # Mostrar notificación del último envase primero
        if eventos_ultimo_envase:
            for evento in eventos_ultimo_envase:
                messagebox.showinfo("Atención Último Envase", evento)

        # Mostrar notificaciones de reposición después
        if eventos_reposicion:
            for evento in eventos_reposicion:
                messagebox.showinfo("Reposiciones del Día", evento)

    # Asociar clic al calendario
    calendar.bind("<<CalendarSelected>>", mostrar_notificacion_evento)

    return nueva_ultima_actualizacion

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
    ventana_todos.geometry("900x600")  # Aumentar el tamaño de la ventana para una mejor vista
    ventana_todos.configure(bg="#50C878")  # Fondo verde claro

    # Frame para organizar todos los widgets
    frame_contenedor = Frame(ventana_todos, bg="#50C878")
    frame_contenedor.pack(fill=BOTH, expand=True, padx=20, pady=20)

    # Título de la ventana
    Label(frame_contenedor, text="Lista de Todos los Pacientes", font=("Arial", 16, "bold"), bg="#50C878", fg="white").pack(pady=10)

    # Frame para Treeview y Scrollbar
    frame = Frame(frame_contenedor, bg="#50C878")
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
        columns=("ID", "Nombre", "Apellidos", "Teléfono"),
        show="headings",  # Mostrar solo encabezados para nodos principales
        yscrollcommand=scrollbar_y.set,
        xscrollcommand=scrollbar_x.set
    )
    tree.pack(fill=BOTH, expand=True)

    # Configuración de las columnas
    tree.heading("ID", text="ID")
    tree.heading("Nombre", text="Nombre")
    tree.heading("Apellidos", text="Apellidos")
    tree.heading("Teléfono", text="Teléfono")
    tree.column("ID", width=50, anchor="center")
    tree.column("Nombre", width=200, anchor="center")
    tree.column("Apellidos", width=200, anchor="center")
    tree.column("Teléfono", width=150, anchor="center")

    # Estilo para Treeview con colores alternos en filas y selección
    style = ttk.Style()
    style.theme_use("default")
    style.configure(
        "Treeview",
        background="white",
        foreground="black",
        rowheight=30,
        fieldbackground="white",
        font=("Arial", 12)
    )
    style.map(
        "Treeview",
        background=[("selected", "#50C878")],  # Verde para selección
        foreground=[("selected", "white")]
    )

    # Estilo especial para las medicaciones (nodos hijos)
    style.configure("Treeview.Child", foreground="#555555", font=("Arial", 10, "italic"))

    # Vincular scrollbars con el Treeview
    scrollbar_y.config(command=tree.yview)
    scrollbar_x.config(command=tree.xview)

    # Obtener datos de la base de datos
    try:
        conn = sqlite3.connect("pacientes.db")
        cursor = conn.cursor()

        # Obtener pacientes
        cursor.execute("""
            SELECT id, nombre, apellidos, telefono
            FROM Pacientes
            ORDER BY apellidos ASC
        """)
        pacientes = cursor.fetchall()

        # Insertar pacientes como nodos principales
        for paciente in pacientes:
            paciente_id, nombre, apellidos, telefono = paciente
            parent_id = tree.insert("", END, values=(paciente_id, nombre, apellidos, telefono))

            # Obtener medicaciones del paciente
            cursor.execute("""
                SELECT medicacion, cn, fecha_inicio, fecha_fin, posologia
                FROM Medicaciones
                WHERE paciente_id = ?
            """, (paciente_id,))
            medicaciones = cursor.fetchall()

            # Insertar medicaciones como nodos hijos del paciente
            for medicacion in medicaciones:
                medicacion_nombre, cn, fecha_inicio, fecha_fin, posologia = medicacion
                tree.insert(
                    parent_id,
                    END,
                    values=(f"Medicamento: {medicacion_nombre} (CN: {cn})",
                            f"Inicio: {fecha_inicio}",
                            f"Fin: {fecha_fin}",
                            f"Posología: {posologia}"),
                    tags=("child",)  # Estilo especial para medicaciones
                )

        conn.close()

    except sqlite3.Error as e:
        messagebox.showerror("Error de base de datos", f"No se pudo cargar los datos: {e}")

    # Botón para cerrar la ventana
    boton_cerrar = Button(
        frame_contenedor,
        text="Cerrar",
        command=ventana_todos.destroy,
        bg="#007C5C",  # Verde oscuro
        fg="white",
        font=("Arial", 12)
    )
    boton_cerrar.pack(pady=10)

    # Actualizar colores del calendario después de cerrar la ventana de pacientes
    def refrescar_calendario():
        global ultima_actualizacion
        ultima_actualizacion = marcar_dias_medicacion(calendar, ultima_actualizacion)  # Vuelve a marcar los días en el calendario

    ventana_todos.protocol("WM_DELETE_WINDOW", refrescar_calendario)  # Asegura que se refresque al cerrar la ventana


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

        # Frame contenedor para organizar mejor los widgets
        frame_contenedor = Frame(ventana, bg="#50C878")
        frame_contenedor.pack(fill=BOTH, expand=True, padx=20, pady=20)

        # Título de la ventana
        Label(frame_contenedor, text=f"Información de {paciente[1]} {paciente[2]}", font=("Arial", 16, "bold"), bg="#50C878", fg="white").grid(row=0, column=0, columnspan=2, pady=10)

        # Datos del paciente
        Label(frame_contenedor, text=f"Nombre:", font=("Arial", 12), bg="#50C878", anchor="w").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        Label(frame_contenedor, text=f"{paciente[1]}", font=("Arial", 12), bg="#50C878").grid(row=1, column=1, padx=5, pady=5, sticky="w")

        Label(frame_contenedor, text=f"Apellidos:", font=("Arial", 12), bg="#50C878", anchor="w").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        Label(frame_contenedor, text=f"{paciente[2]}", font=("Arial", 12), bg="#50C878").grid(row=2, column=1, padx=5, pady=5, sticky="w")

        Label(frame_contenedor, text=f"Teléfono:", font=("Arial", 12), bg="#50C878", anchor="w").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        Label(frame_contenedor, text=f"{paciente[3]}", font=("Arial", 12), bg="#50C878").grid(row=3, column=1, padx=5, pady=5, sticky="w")

        Label(frame_contenedor, text=f"Número de Tarjeta:", font=("Arial", 12), bg="#50C878", anchor="w").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        Label(frame_contenedor, text=f"{paciente[4]}", font=("Arial", 12), bg="#50C878").grid(row=4, column=1, padx=5, pady=5, sticky="w")

        # Sección de Medicaciones
        Label(frame_contenedor, text="Medicaciones:", font=("Arial", 14, "bold"), bg="#50C878", fg="white").grid(row=5, column=0, columnspan=2, pady=10)

        if medicaciones:
            for idx, medicacion in enumerate(medicaciones, start=6):
                texto = f"{medicacion[0]} (CN: {medicacion[1]}), {medicacion[2]} - {medicacion[3]} ({medicacion[4]} tomas/día)"
                Label(frame_contenedor, text=texto, font=("Arial", 12), bg="#50C878", anchor="w").grid(row=idx, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        else:
            Label(frame_contenedor, text="Este paciente no tiene medicaciones registradas.", font=("Arial", 12), bg="#50C878", anchor="w").grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Botón para editar el paciente
        Button(frame_contenedor, text="Editar Paciente", command=lambda: editar_paciente_desde_lista(ventana, paciente_id), bg="#007C5C", fg="white", font=("Arial", 12)).grid(row=len(medicaciones) + 7, column=0, columnspan=2, pady=20)

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

        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Paciente actualizado correctamente.")
        ventana.destroy()

    def eliminar_medicacion():
        seleccion = lista_medicaciones.curselection()
        if not seleccion:
            messagebox.showwarning("Seleccionar medicación", "Debe seleccionar una medicación para eliminar.")
            return

        # Obtener el ID de la medicación seleccionada
        medicacion_id = medicaciones[seleccion[0]]['id']

        # Eliminar de la base de datos
        conn = sqlite3.connect("pacientes.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Medicaciones WHERE id = ?", (medicacion_id,))
        conn.commit()
        conn.close()

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
                "id": None,  # Esto se actualizará si se está editando
                "medicamento": medicamento,
                "cn": cn,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "posologia": posologia,
                "unidades_por_caja": unidades_por_caja,
            }

            conn = sqlite3.connect("pacientes.db")
            cursor = conn.cursor()

            if accion == "añadir":
                # Insertar nueva medicación en la base de datos
                cursor.execute("""
                    INSERT INTO Medicaciones (
                        paciente_id, medicacion, cn, fecha_inicio, fecha_fin, posologia, unidades_por_caja, ultima_actualizacion
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (paciente_id, medicamento, cn, fecha_inicio, fecha_fin, posologia, unidades_por_caja))
                conn.commit()
                nueva_medicacion["id"] = cursor.lastrowid  # Obtener el ID generado
                medicaciones.append(nueva_medicacion)

                # Actualizar la interfaz
                lista_medicaciones.insert(
                    END,
                    f"{medicamento} (CN: {cn}) - {fecha_inicio} a {fecha_fin} ({posologia} tomas/día, {unidades_por_caja} unidades/caja)"
                )
            elif accion == "editar" and indice is not None:
                # Actualizar la medicación en la base de datos
                medicacion_id = medicaciones[indice]['id']
                cursor.execute("""
                    UPDATE Medicaciones
                    SET medicacion = ?, cn = ?, fecha_inicio = ?, fecha_fin = ?, posologia = ?, unidades_por_caja = ?, ultima_actualizacion = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (medicamento, cn, fecha_inicio, fecha_fin, posologia, unidades_por_caja, medicacion_id))
                conn.commit()

                # Actualizar la medicación en la lista en memoria
                medicaciones[indice] = nueva_medicacion
                medicaciones[indice]['id'] = medicacion_id

                # Actualizar la interfaz
                lista_medicaciones.delete(indice)
                lista_medicaciones.insert(
                    indice,
                    f"{medicamento} (CN: {cn}) - {fecha_inicio} a {fecha_fin} ({posologia} tomas/día, {unidades_por_caja} unidades/caja)"
                )

            conn.close()
            messagebox.showinfo("Éxito", "Cambios guardados correctamente.")
            ventana_medicacion.destroy()

        # Configurar ventana
        ventana_medicacion = Toplevel()
        ventana_medicacion.title(f"{'Añadir' if accion == 'añadir' else 'Editar'} Medicación")
        ventana_medicacion.geometry("1024x768")
        ventana_medicacion.configure(bg="#50C878")

        # Crear frame para el contenido
        frame_contenido = Frame(ventana_medicacion, bg="#50C878")
        frame_contenido.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Etiquetas y campos de entrada para la medicación
        Label(frame_contenido, text="Medicamento:", bg="#50C878", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10)
        entry_medicamento = Entry(frame_contenido, font=("Arial", 12))
        entry_medicamento.grid(row=0, column=1, padx=10, pady=10)

        Label(frame_contenido, text="CN (opcional):", bg="#50C878", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10)
        entry_cn = Entry(frame_contenido, font=("Arial", 12))
        entry_cn.grid(row=1, column=1, padx=10, pady=10)

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

        Label(frame_contenido, text="Fecha de inicio:", bg="#50C878", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=10)
        calendar_inicio = Calendar(
            frame_contenido, selectmode="day", date_pattern="dd-mm-yyyy",
            year=fecha_inicio_dt.year, month=fecha_inicio_dt.month, day=fecha_inicio_dt.day, locale="es_ES"
        )
        calendar_inicio.grid(row=2, column=1, padx=10, pady=10)

        Label(frame_contenido, text="Fecha de fin:", bg="#50C878", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=10)
        calendar_fin = Calendar(
            frame_contenido, selectmode="day", date_pattern="dd-mm-yyyy",
            year=fecha_fin_dt.year, month=fecha_fin_dt.month, day=fecha_fin_dt.day, locale="es_ES"
        )
        calendar_fin.grid(row=3, column=1, padx=10, pady=10)

        Label(frame_contenido, text="Posología (tomas/día):", bg="#50C878", font=("Arial", 12)).grid(row=4, column=0, padx=10, pady=10)
        entry_posologia = Entry(frame_contenido, font=("Arial", 12))
        entry_posologia.grid(row=4, column=1, padx=10, pady=10)

        Label(frame_contenido, text="Unidades por caja:", bg="#50C878", font=("Arial", 12)).grid(row=5, column=0, padx=10, pady=10)
        entry_unidades = Entry(frame_contenido, font=("Arial", 12))
        entry_unidades.grid(row=5, column=1, padx=10, pady=10)

        # Precargar otros datos si es una edición
        if accion == "editar" and indice is not None:
            entry_posologia.insert(0, medicacion["posologia"])
            entry_unidades.insert(0, medicacion["unidades_por_caja"])

        # Botón para guardar los cambios
        Button(
            frame_contenido,
            text="Guardar",
            command=guardar,
            bg="#007C5C",
            fg="white",
            font=("Arial", 12)
        ).grid(row=6, column=0, columnspan=2, pady=20)

    # Obtener datos actuales del paciente
    conn = sqlite3.connect("pacientes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Pacientes WHERE id = ?", (paciente_id,))
    paciente = cursor.fetchone()

    cursor.execute("""
        SELECT id, medicacion, cn, fecha_inicio, fecha_fin, posologia, unidades_por_caja
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
    frame_contenido = Frame(ventana, bg="#50C878")
    frame_contenido.pack(fill=BOTH, expand=True, padx=10, pady=20)

    Label(frame_contenido, text="Nombre:", bg="#50C878", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10)
    entry_nombre = Entry(frame_contenido, font=("Arial", 12))
    entry_nombre.insert(0, paciente[1])
    entry_nombre.grid(row=0, column=1, padx=10, pady=10)

    Label(frame_contenido, text="Apellidos:", bg="#50C878", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10)
    entry_apellidos = Entry(frame_contenido, font=("Arial", 12))
    entry_apellidos.insert(0, paciente[2])
    entry_apellidos.grid(row=1, column=1, padx=10, pady=10)

    Label(frame_contenido, text="Teléfono:", bg="#50C878", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=10)
    entry_telefono = Entry(frame_contenido, font=("Arial", 12))
    entry_telefono.insert(0, paciente[3])
    entry_telefono.grid(row=2, column=1, padx=10, pady=10)

    Label(frame_contenido, text="Número de Tarjeta:", bg="#50C878", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=10)
    entry_tarjeta = Entry(frame_contenido, font=("Arial", 12))
    entry_tarjeta.insert(0, paciente[4])
    entry_tarjeta.grid(row=3, column=1, padx=10, pady=10)

    # Crear lista para las medicaciones
    lista_medicaciones = Listbox(frame_contenido, height=10, width=75, font=("Arial", 12))
    lista_medicaciones.grid(row=5, column=0, columnspan=2, padx=10, pady=20)

    # Cargar medicaciones
    medicaciones = []
    for medicacion in medicaciones_db:
        lista_medicaciones.insert(
            END,
            f"{medicacion[1]} (CN: {medicacion[2]}) - {medicacion[3]} a {medicacion[4]} ({medicacion[5]} tomas/día, {medicacion[6]} unidades/caja)"
        )
        medicaciones.append({
            "id": medicacion[0],
            "medicamento": medicacion[1],
            "cn": medicacion[2],
            "fecha_inicio": medicacion[3],
            "fecha_fin": medicacion[4],
            "posologia": medicacion[5],
            "unidades_por_caja": medicacion[6],
        })

    # Vincular doble clic en la lista de medicaciones
    lista_medicaciones.bind("<Double-1>", lambda event: abrir_ventana_medicacion("editar", lista_medicaciones.curselection()[0]))

    # Botones para añadir, eliminar y guardar cambios
    Button(frame_contenido, text="Eliminar Medicación", command=eliminar_medicacion, bg="#E74C3C", fg="white", font=("Arial", 12)).grid(row=6, column=1, padx=10, pady=20, sticky="e")
    Button(frame_contenido, text="Añadir Medicación", command=lambda: abrir_ventana_medicacion("añadir"), bg="#007C5C", fg="white", font=("Arial", 12)).grid(row=6, column=0, padx=10, pady=20, sticky="w")
    Button(frame_contenido, text="Guardar Cambios", command=guardar_paciente, bg="#007C5C", fg="white", font=("Arial", 12)).grid(row=7, column=0, columnspan=2, pady=20)

# Función para exportar datos a CSV o Excel
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
            SELECT p.nombre, p.apellidos, m.medicacion, m.cn, m.fecha_inicio, m.fecha_fin, m.posologia, m.unidades_por_caja, m.ultima_actualizacion
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
                writer.writerow(["Nombre", "Apellidos", "Medicamento", "CN", "Fecha Inicio", "Fecha Fin", "Posología", "Unidades por Caja", "Última Actualización"])
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
                    columns=["Nombre", "Apellidos", "Medicamento", "CN", "Fecha Inicio", "Fecha Fin", "Posología", "Unidades por Caja", "Última Actualización"]
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
    ventana_aviso.geometry("800x700")  # Tamaño actualizado
    ventana_aviso.configure(bg="#50C878")

    # Frame principal de la ventana
    frame_principal = Frame(ventana_aviso, bg="#50C878")
    frame_principal.pack(fill=BOTH, expand=True, padx=20, pady=20)

    # Campo de búsqueda por nombre del paciente
    Label(frame_principal, text="Buscar paciente por nombre:", bg="#50C878", fg="white", font=("Arial", 12)).pack(pady=10)
    entry_nombre = Entry(frame_principal, width=30, font=("Arial", 12))
    entry_nombre.pack(pady=5)

    # Lista de sugerencias
    lista_sugerencias = Listbox(frame_principal, height=5, width=50, font=("Arial", 12))
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
    Label(frame_principal, text="Número de teléfono del paciente:", bg="#50C878", fg="white", font=("Arial", 12)).pack(pady=10)
    entry_telefono = Entry(frame_principal, width=30, font=("Arial", 12))
    entry_telefono.pack(pady=5)

    # Campo de texto para escribir el mensaje
    Label(frame_principal, text="Escribir mensaje:", bg="#50C878", fg="white", font=("Arial", 12)).pack(pady=10)
    text_mensaje = Text(frame_principal, width=50, height=10, font=("Arial", 12))
    text_mensaje.pack(pady=5)

    # Scrollbar para el campo de texto
    scrollbar = Scrollbar(frame_principal, orient="vertical", command=text_mensaje.yview)
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

    Button(frame_principal, text="Enviar Mensaje por WhatsApp", command=enviar_whatsapp, bg="#007C5C", fg="white", font=("Arial", 12), width=25).pack(pady=20)


# Configuración principal
from tkcalendar import Calendar

def main():
    # Configuración inicial
    root = Tk()
    root.title("Gestión de Medicaciones")
    root.configure(bg="#50C878")
    root.geometry("1024x768")  # Aumentar el tamaño de la ventana

    # Crear un Frame contenedor principal
    frame_contenedor = Frame(root, bg="#50C878")
    frame_contenedor.pack(side=LEFT, fill=BOTH, expand=True)

    # Crear un Scrollbar para la ventana principal
    scrollbar = Scrollbar(root, orient=VERTICAL)
    scrollbar.pack(side=RIGHT, fill=Y)

    # Calendario en Español
    calendar = Calendar(
        frame_contenedor,
        selectmode="day", 
        date_pattern="dd-mm-yyyy", 
        background="#50C878", 
        foreground="white",
        locale="es_ES"  # Cambiar el idioma a Español
    )
    calendar.pack(fill=BOTH, expand=True, padx=20, pady=20)  # Hace el calendario más grande

    # Inicializar variable de última actualización
    ultima_actualizacion = None  # Variable para rastrear actualizaciones
    ultima_actualizacion = marcar_dias_medicacion(calendar, ultima_actualizacion)  # Inicializar calendario

    # Marcar eventos iniciales
    calendar.bind("<<CalendarSelected>>", lambda event: ver_medicacion_dia(calendar.get_date()))

    # Función para refrescar el calendario
    def refrescar_calendario():
        nonlocal ultima_actualizacion
        ultima_actualizacion = marcar_dias_medicacion(calendar, ultima_actualizacion)  # Vuelve a marcar los días en el calendario

    # Frame para los botones
    frame_botones = Frame(frame_contenedor, bg="#50C878")
    frame_botones.pack(fill=BOTH, expand=True, padx=10, pady=20)

    # Botones principales
    Button(frame_botones, text="Añadir Paciente", command=lambda: añadir_paciente(root, calendar), bg="#007C5C", fg="white", font=("Arial", 12), width=25).pack(pady=5)
    Button(frame_botones, text="Ver Todos los Pacientes", command=ver_todos_pacientes, bg="#007C5C", fg="white", font=("Arial", 12), width=25).pack(pady=5)
    Button(frame_botones, text="Exportar a CSV o Excel", command=exportar_datos, bg="#007C5C", fg="white", font=("Arial", 12), width=25).pack(pady=5)
    Button(frame_botones, text="Copia de Seguridad", command=backup_database, bg="#007C5C", fg="white", font=("Arial", 12), width=25).pack(pady=5)
    Button(frame_botones, text="Avisar al Paciente por Whatsapp", command=abrir_ventana_aviso_paciente, bg="#007C5C", fg="white", font=("Arial", 12), width=25).pack(pady=5)

    # **Nuevo botón para refrescar el calendario**
    Button(frame_botones, text="Refrescar Calendario", command=refrescar_calendario, bg="#FF5733", fg="white", font=("Arial", 12), width=25).pack(pady=10)

    # Búsqueda de pacientes
    frame_busqueda = Frame(frame_contenedor, bg="#50C878")
    frame_busqueda.pack(pady=10)

    # Etiqueta para la búsqueda
    Label(frame_busqueda, text="Búsqueda de Pacientes:", bg="#50C878", fg="white", font=("Arial", 12)).pack(side=LEFT, padx=5)

    # Entrada de búsqueda
    entry_busqueda = Entry(frame_busqueda, font=("Arial", 12))
    entry_busqueda.pack(side=LEFT, padx=5)

    # Botón de limpiar búsqueda
    Button(frame_busqueda, text="Limpiar", 
            command=lambda: (entry_busqueda.delete(0, END), lista_sugerencias.delete(0, END)),
            bg="#E74C3C", fg="white", font=("Arial", 12)).pack(side=LEFT, padx=5)

    # Lista de sugerencias con scroll
    frame_lista = Frame(frame_contenedor, bg="#50C878")
    frame_lista.pack(pady=10)

    lista_sugerencias = Listbox(frame_lista, height=10, width=50, font=("Arial", 12))
    lista_sugerencias.pack(side=LEFT, padx=5)

    # Vinculamos el scrollbar al Listbox
    scrollbar_lista = Scrollbar(frame_lista, orient=VERTICAL, command=lista_sugerencias.yview)
    scrollbar_lista.pack(side=LEFT, fill=Y)
    lista_sugerencias.config(yscrollcommand=scrollbar_lista.set)

    # Eventos para la búsqueda
    entry_busqueda.bind("<KeyRelease>", lambda event: buscar_paciente_autocompletar(entry_busqueda, lista_sugerencias))
    entry_busqueda.bind("<Return>", lambda event: buscar_paciente_autocompletar(entry_busqueda, lista_sugerencias))
    lista_sugerencias.bind("<Double-1>", lambda event: mostrar_informacion_paciente(int(lista_sugerencias.get(ACTIVE).split("- ID: ")[1])))

    # Copyright en la parte inferior derecha
    copyright_label = Label(root, text="© PharmaJava", bg="#50C878", fg="white", font=("Arial", 10))
    copyright_label.pack(side="bottom", anchor="e", padx=10, pady=10)

    root.mainloop()

# Inicializar base de datos y lanzar programa
if __name__ == "__main__":
    init_db()
    main()
