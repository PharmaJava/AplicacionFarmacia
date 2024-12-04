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
import matplotlib.pyplot as plt
import seaborn as sns

# Inicializar base de datos
def init_db():
    """
    Inicializa la base de datos y crea las tablas necesarias si no existen.
    Incluye la columna 'intervalo_dias' directamente en la definición de la tabla Medicaciones.
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

    # Crear tabla Medicaciones con la columna 'ultima_actualizacion' y 'intervalo_dias'
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
            intervalo_dias REAL NOT NULL,  -- Intervalo en días (puede ser decimal)
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
            intervalo_dias = medicacion["intervalo_dias"]  # Intervalo en días

            # Insertar la medicación
            cursor.execute("""
                INSERT INTO Medicaciones (
                    paciente_id, medicacion, cn, fecha_inicio, fecha_fin, posologia, unidades_por_caja, intervalo_dias, ultima_actualizacion
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (paciente_id, medicamento, cn, fecha_inicio, fecha_fin, posologia, unidades_por_caja, intervalo_dias))

            # Actualizar el calendario con las fechas de reabastecimiento
            marcar_dias_reabastecimiento(calendar, nombre, medicamento, fecha_inicio, fecha_fin, posologia, unidades_por_caja, intervalo_dias)

        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Paciente y medicaciones guardados correctamente.")
        ventana.destroy()

    def marcar_dias_reabastecimiento(calendar, nombre, medicamento, fecha_inicio, fecha_fin, posologia, unidades_por_caja, intervalo_dias):
        """Marca en el calendario las fechas de reabastecimiento con información del paciente y medicación."""

        # Validar y asignar valor predeterminado si intervalo_dias es 0, negativo o None
        if intervalo_dias is None or intervalo_dias <= 0:
            intervalo_dias = 1  # Valor predeterminado

        # Validar otros datos de entrada
        if posologia <= 0 or unidades_por_caja <= 0:
            messagebox.showwarning(
                "Datos inválidos",
                "Posología y unidades por caja deben ser mayores que 0."
            )
            return

        try:
            # Convertir fechas al formato datetime
            fecha_actual = datetime.strptime(fecha_inicio, "%d-%m-%Y")
            fecha_final = datetime.strptime(fecha_fin, "%d-%m-%Y")
        except ValueError:
            messagebox.showerror(
                "Error de formato de fecha",
                "Las fechas deben estar en el formato DD-MM-YYYY."
            )
            return

        # Validar el rango de fechas
        if fecha_actual > fecha_final:
            messagebox.showwarning(
                "Rango de fechas inválido",
                "La fecha de inicio no puede ser posterior a la fecha de fin."
            )
            return

        # Calcular la frecuencia de reposición en días (permitiendo valores decimales)
        frecuencia_reposicion = (unidades_por_caja / posologia) * intervalo_dias

        # Validar que la frecuencia calculada sea válida
        if frecuencia_reposicion <= 0:
            messagebox.showwarning(
                "Frecuencia de reposición inválida",
                "La frecuencia calculada es inválida. Verifique los datos ingresados."
            )
            return

        # Añadir el primer evento (día de inicio)
        evento = f"Paciente: {nombre}, Medicación: {medicamento}"
        calendar.calevent_create(fecha_actual, evento, "reposición")

        # Iterar y marcar eventos en el rango hasta la fecha final
        while fecha_actual <= fecha_final:
            # Incrementar la fecha actual por la frecuencia (incluso con decimales)
            fecha_actual += timedelta(days=frecuencia_reposicion)
            if fecha_actual <= fecha_final:
                calendar.calevent_create(fecha_actual, evento, "reposición")

        # Configurar el color del evento
        calendar.tag_config("reposición", background="red", foreground="white")



    def añadir_medicacion():
        def guardar_medicacion():
            medicamento = entry_medicamento.get()
            cn = entry_cn.get()
            fecha_inicio = calendar_inicio.get_date()
            fecha_fin = calendar_fin.get_date()

            try:
                # Permitir el uso de números decimales para la posología y el intervalo
                posologia = float(entry_posologia.get())
                unidades_por_caja = int(entry_unidades.get())

                # Comprobar si el campo intervalo está vacío y asignar 0 si es el caso
                intervalo_dias_str = entry_intervalo.get()
                intervalo_dias = float(intervalo_dias_str) if intervalo_dias_str else 0
            except ValueError:
                messagebox.showwarning("Datos inválidos", "Posología debe ser un número, unidades por caja debe ser un entero y el intervalo debe ser un número.")
                return

            if not medicamento or not fecha_inicio or not fecha_fin or posologia <= 0 or unidades_por_caja <= 0 or intervalo_dias < 0:
                messagebox.showwarning("Datos incompletos", "Debe ingresar todos los datos de la medicación.")
                return

            medicaciones.append({
                "medicamento": medicamento,
                "cn": cn,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "posologia": posologia,
                "unidades_por_caja": unidades_por_caja,
                "intervalo_dias": intervalo_dias  # Guardar intervalo
            })
            lista_medicaciones.insert(
                END, f"{medicamento} (CN: {cn}) - {fecha_inicio} a {fecha_fin} ({posologia} tomas/día, {unidades_por_caja} unidades/caja, {intervalo_dias} días de intervalo)"
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

        Label(ventana_medicacion, text="Intervalo entre dosis (días):", bg="#50C878", font=("Arial", 12)).grid(row=6, column=0, padx=10, pady=10)
        entry_intervalo = Entry(ventana_medicacion, font=("Arial", 12))
        entry_intervalo.grid(row=6, column=1, padx=10, pady=10)

        Button(ventana_medicacion, text="Guardar Medicación", command=guardar_medicacion, bg="#007C5C", fg="white", font=("Arial", 12)).grid(row=7, column=0, columnspan=2, pady=20)

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
    """
    # Eliminar eventos antiguos
    calendar.calevent_remove("reposición")
    calendar.calevent_remove("ultimo_envase")

    conn = sqlite3.connect("pacientes.db")
    cursor = conn.cursor()

    # Consultar medicaciones actualizadas después de la última modificación, si aplica
    query = """
        SELECT p.nombre, m.fecha_inicio, m.fecha_fin, m.posologia, m.unidades_por_caja, m.medicacion, m.ultima_actualizacion, m.intervalo_dias
        FROM Medicaciones m
        INNER JOIN Pacientes p ON p.id = m.paciente_id
    """
    if ultima_actualizacion:
        query += " WHERE m.ultima_actualizacion > ?"
        cursor.execute(query, (ultima_actualizacion,))
    else:
        cursor.execute(query)

    medicaciones = cursor.fetchall()
    conn.close()

    # Procesar los datos y marcarlos en el calendario
    for medicacion in medicaciones:
        nombre_paciente, fecha_inicio, fecha_fin, posologia, unidades_por_caja, nombre_medicacion, _, intervalo_dias = medicacion

        # Validar y ajustar valores predeterminados
        if posologia <= 0 or unidades_por_caja <= 0:
            continue  # Omitir medicaciones con datos inválidos

        # Asignar un valor predeterminado si intervalo_dias es 0 o menor
        intervalo_dias = max(1, intervalo_dias)

        try:
            inicio = datetime.strptime(fecha_inicio, "%d-%m-%Y")
            fin = datetime.strptime(fecha_fin, "%d-%m-%Y")
        except ValueError:
            continue  # Omitir medicaciones con fechas mal formateadas

        if inicio > fin:
            continue  # Omitir medicaciones con un rango de fechas inválido

        # Calcular la frecuencia de reposición en días
        frecuencia_reposicion = (unidades_por_caja / posologia) * intervalo_dias

        if frecuencia_reposicion <= 0:
            continue  # Omitir medicaciones con frecuencias inválidas

        actual = inicio
        while actual <= fin:
            # Último envase
            if actual + timedelta(days=frecuencia_reposicion) > fin:
                calendar.calevent_create(
                    actual,
                    f"Último Envase de {nombre_medicacion} - Paciente: {nombre_paciente}",
                    "ultimo_envase"
                )
            else:  # Reposición
                calendar.calevent_create(
                    actual,
                    f"Reposición de {nombre_medicacion} - Paciente: {nombre_paciente}",
                    "reposición"
                )
            actual += timedelta(days=frecuencia_reposicion)

    # Configurar colores
    calendar.tag_config("reposición", background="red", foreground="white")
    calendar.tag_config("ultimo_envase", background="green", foreground="white")

    return ultima_actualizacion

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
    ventana_todos.geometry("1024x768")  # Aumentar el tamaño de la ventana para una mejor vista
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

            # Obtener medicaciones del paciente, incluyendo el intervalo de días
            cursor.execute("""
                SELECT medicacion, cn, fecha_inicio, fecha_fin, posologia, intervalo_dias
                FROM Medicaciones
                WHERE paciente_id = ?
            """, (paciente_id,))
            medicaciones = cursor.fetchall()

            # Insertar medicaciones como nodos hijos del paciente
            for medicacion in medicaciones:
                medicacion_nombre, cn, fecha_inicio, fecha_fin, posologia, intervalo_dias = medicacion
                tree.insert(
                    parent_id,
                    END,
                    values=(f"Medicamento: {medicacion_nombre} (CN: {cn})",
                            f"Inicio: {fecha_inicio}",
                            f"Fin: {fecha_fin}",
                            f"Posología: {posologia}, Intervalo: {intervalo_dias} días"),
                    tags=("child",)  # Estilo especial para medicaciones
                )

        conn.close()

    except sqlite3.Error as e:
        messagebox.showerror("Error de base de datos", f"No se pudo cargar los datos: {e}")

    # Botón para cerrar la ventana
    def refrescar_calendario():
        global ultima_actualizacion
        ultima_actualizacion = marcar_dias_medicacion(calendar, ultima_actualizacion)  # Vuelve a marcar los días en el calendario

    boton_cerrar = Button(
        frame_contenedor,
        text="Cerrar",
        command=lambda: [ventana_todos.destroy(), refrescar_calendario()],
        bg="#007C5C",  # Verde oscuro
        fg="white",
        font=("Arial", 12)
    )
    boton_cerrar.pack(pady=10)

    # Asegurarse de que el calendario se actualice al cerrar la ventana de pacientes
    ventana_todos.protocol("WM_DELETE_WINDOW", lambda: [ventana_todos.destroy(), refrescar_calendario()])  # Asegura que se refresque al cerrar la ventana

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
            SELECT medicacion, cn, fecha_inicio, fecha_fin, posologia, unidades_por_caja, intervalo_dias
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
                # Mostrar medicación con el intervalo de días
                fecha_fin = datetime.strptime(medicacion[3], "%d-%m-%Y")
                intervalo_dias = medicacion[6]

                # Calcular la fecha de la última dispensación
                ultima_dispensacion = fecha_fin + timedelta(days=intervalo_dias)
                hoy = datetime.now()

                # Verificar si es la última dispensación
                mensaje_extra = ""
                if ultima_dispensacion.date() <= hoy.date():
                    mensaje_extra = " - ¡Última Dispensación!"

                texto = f"{medicacion[0]} (CN: {medicacion[1]}), {medicacion[2]} - {medicacion[3]} ({medicacion[4]} tomas/día, {medicacion[5]} unidades/caja, {medicacion[6]} días de intervalo){mensaje_extra}"
                Label(frame_contenedor, text=texto, font=("Arial", 12), bg="#50C878", anchor="w").grid(row=idx, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        else:
            Label(frame_contenedor, text="Este paciente no tiene medicaciones registradas.", font=("Arial", 12), bg="#50C878", anchor="w").grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Botón para editar el paciente
        Button(frame_contenedor, text="Editar Paciente", command=lambda: editar_paciente_desde_lista(ventana, paciente_id, calendar=0), bg="#007C5C", fg="white", font=("Arial", 12)).grid(row=len(medicaciones) + 7, column=0, columnspan=2, pady=20)

    except sqlite3.Error as e:
        messagebox.showerror("Error de base de datos", str(e))

def editar_paciente_desde_lista(root, paciente_id, calendar):
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
                posologia = float(entry_posologia.get())
                unidades_por_caja = int(entry_unidades.get())
                intervalo_dias = float(entry_intervalo.get())  # Mantener como número
            except ValueError:
                messagebox.showwarning("Datos inválidos", "Posología debe ser un número, unidades por caja debe ser un entero y el intervalo debe ser un número.")
                return

            if not medicamento or not fecha_inicio or not fecha_fin or posologia <= 0 or unidades_por_caja <= 0 or intervalo_dias < 0:
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
                "intervalo_dias": intervalo_dias,  # Guardar intervalo correctamente
            }

            conn = sqlite3.connect("pacientes.db")
            cursor = conn.cursor()

            if accion == "añadir":
                # Insertar nueva medicación en la base de datos
                cursor.execute("""
                    INSERT INTO Medicaciones (
                        paciente_id, medicacion, cn, fecha_inicio, fecha_fin, posologia, unidades_por_caja, intervalo_dias, ultima_actualizacion
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (paciente_id, medicamento, cn, fecha_inicio, fecha_fin, posologia, unidades_por_caja, intervalo_dias))
                conn.commit()
                nueva_medicacion["id"] = cursor.lastrowid  # Obtener el ID generado
                medicaciones.append(nueva_medicacion)

                # Actualizar la interfaz
                lista_medicaciones.insert(
                    END,
                    f"{medicamento} (CN: {cn}) - {fecha_inicio} a {fecha_fin} ({posologia} tomas/día, {unidades_por_caja} unidades/caja, intervalo: {intervalo_dias} días)"
                )
            elif accion == "editar" and indice is not None:
                # Actualizar la medicación en la base de datos
                medicacion_id = medicaciones[indice]['id']
                cursor.execute("""
                    UPDATE Medicaciones
                    SET medicacion = ?, cn = ?, fecha_inicio = ?, fecha_fin = ?, posologia = ?, unidades_por_caja = ?, intervalo_dias = ?, ultima_actualizacion = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (medicamento, cn, fecha_inicio, fecha_fin, posologia, unidades_por_caja, intervalo_dias, medicacion_id))
                conn.commit()

                # Actualizar la medicación en la lista en memoria
                medicaciones[indice] = nueva_medicacion
                medicaciones[indice]['id'] = medicacion_id

                # Actualizar la interfaz
                lista_medicaciones.delete(indice)
                lista_medicaciones.insert(
                    indice,
                    f"{medicamento} (CN: {cn}) - {fecha_inicio} a {fecha_fin} ({posologia} tomas/día, {unidades_por_caja} unidades/caja, intervalo: {intervalo_dias} días)"
                )

            conn.close()

            # Mostrar mensaje de éxito
            messagebox.showinfo("Éxito", f"Medicamento {'añadido' if accion == 'añadir' else 'editado'} correctamente.")
            ventana_medicacion.destroy()

        # Configurar ventana de edición
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

        Label(frame_contenido, text="Intervalo entre dosis (días):", bg="#50C878", font=("Arial", 12)).grid(row=6, column=0, padx=10, pady=10)
        entry_intervalo = Entry(frame_contenido, font=("Arial", 12))
        entry_intervalo.grid(row=6, column=1, padx=10, pady=10)

        # Precargar otros datos si es una edición
        if accion == "editar" and indice is not None:
            entry_posologia.insert(0, medicacion["posologia"])
            entry_unidades.insert(0, medicacion["unidades_por_caja"])
            entry_intervalo.insert(0, medicacion["intervalo_dias"])

        # Botón para guardar los cambios
        Button(
            frame_contenido,
            text="Guardar",
            command=guardar,
            bg="#007C5C",
            fg="white",
            font=("Arial", 12)
        ).grid(row=7, column=0, columnspan=2, pady=20)

    # Obtener datos actuales del paciente
    conn = sqlite3.connect("pacientes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Pacientes WHERE id = ?", (paciente_id,))
    paciente = cursor.fetchone()

    cursor.execute("""
        SELECT id, medicacion, cn, fecha_inicio, fecha_fin, posologia, unidades_por_caja, intervalo_dias
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
            f"{medicacion[1]} (CN: {medicacion[2]}) - {medicacion[3]} a {medicacion[4]} ({medicacion[5]} tomas/día, {medicacion[6]} unidades/caja, {medicacion[7]} días de intervalo)"
        )
        medicaciones.append({
            "id": medicacion[0],
            "medicamento": medicacion[1],
            "cn": medicacion[2],
            "fecha_inicio": medicacion[3],
            "fecha_fin": medicacion[4],
            "posologia": medicacion[5],
            "unidades_por_caja": medicacion[6],
            "intervalo_dias": medicacion[7],
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

        # Obtener los datos de las medicaciones, incluyendo intervalo_dias
        cursor.execute("""
            SELECT p.nombre, p.apellidos, m.medicacion, m.cn, m.fecha_inicio, m.fecha_fin, m.posologia, m.unidades_por_caja, m.intervalo_dias, m.ultima_actualizacion
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

                # Escribir encabezados para medicaciones, incluyendo el intervalo de días
                writer.writerow(["Nombre", "Apellidos", "Medicamento", "CN", "Fecha Inicio", "Fecha Fin", "Posología", "Unidades por Caja", "Intervalo Días", "Última Actualización"])
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

                # Convertir datos de medicaciones a un DataFrame, incluyendo el intervalo de días
                df_medicaciones = pd.DataFrame(
                    medicaciones,
                    columns=["Nombre", "Apellidos", "Medicamento", "CN", "Fecha Inicio", "Fecha Fin", "Posología", "Unidades por Caja", "Intervalo Días", "Última Actualización"]
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


import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import win32print  # Para manejo de impresoras en Windows
import sqlite3
from datetime import datetime, timedelta
import pandas as pd

# Función global para imprimir los datos
def imprimir_ultimo_envase(tree, ventana_padre):
    try:
        # Crear ventana emergente para seleccionar impresora
        ventana_impresora = tk.Toplevel(ventana_padre)
        ventana_impresora.title("Seleccionar Impresora")
        ventana_impresora.geometry("400x200")
        ventana_impresora.configure(bg="#50C878")

        tk.Label(ventana_impresora, text="Selecciona una impresora:", bg="#50C878", font=("Arial", 12)).pack(pady=10)

        # Obtener lista de impresoras
        impresoras = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
        lista_impresoras = [impresora[2] for impresora in impresoras]

        # Crear combobox para seleccionar la impresora
        seleccion_impresora = tk.StringVar()
        combobox_impresoras = ttk.Combobox(ventana_impresora, textvariable=seleccion_impresora, values=lista_impresoras, state="readonly", width=50)
        combobox_impresoras.pack(pady=10)
        combobox_impresoras.current(0)  # Seleccionar la primera impresora por defecto

        def enviar_a_impresora():
            try:
                seleccion = seleccion_impresora.get()
                if seleccion:
                    # Obtener datos del Treeview
                    texto_a_imprimir = "Último Envase de Medicaciones:\n\n"
                    columnas = ["Paciente", "Medicamento", "Último Envase"]
                    texto_a_imprimir += "\t".join(columnas) + "\n"
                    texto_a_imprimir += "-" * 70 + "\n"

                    for child in tree.get_children():
                        fila = tree.item(child)["values"]
                        texto_a_imprimir += "\t".join(map(str, fila)) + "\n"

                    # Enviar el texto a la impresora seleccionada
                    handle_impresora = win32print.OpenPrinter(seleccion)
                    job = win32print.StartDocPrinter(handle_impresora, 1, ("Último Envase de Medicaciones", None, "RAW"))
                    win32print.StartPagePrinter(handle_impresora)
                    win32print.WritePrinter(handle_impresora, texto_a_imprimir.encode("utf-8"))
                    win32print.EndPagePrinter(handle_impresora)
                    win32print.EndDocPrinter(handle_impresora)
                    win32print.ClosePrinter(handle_impresora)

                    messagebox.showinfo("Éxito", f"Estadísticas enviadas a la impresora: {seleccion}")
                    ventana_impresora.destroy()
                else:
                    messagebox.showwarning("Advertencia", "No se seleccionó ninguna impresora.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo imprimir: {e}")

        # Botón para confirmar la impresión
        tk.Button(ventana_impresora, text="Imprimir", command=enviar_a_impresora, bg="#007C5C", fg="white", font=("Arial", 12)).pack(pady=10)

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir el selector de impresoras: {e}")

# Función global para exportar a Excel
def exportar_a_excel_local(tree):
    try:
        # Obtener los datos del Treeview
        data = []
        for child in tree.get_children():
            row = tree.item(child)["values"]
            data.append(row)

        # Crear un DataFrame de pandas con los datos
        df = pd.DataFrame(data, columns=["Paciente", "Medicamento", "Último Envase"])

        archivo = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if archivo:
            df.to_excel(archivo, index=False, engine="openpyxl")
            messagebox.showinfo("Éxito", f"Archivo exportado correctamente a {archivo}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo exportar a Excel: {e}")

# Función para mostrar el último envase de medicaciones
def mostrar_ultimo_envase():
    # Crear una nueva ventana para mostrar el listado de pacientes y su fecha de último envase
    ventana_ultimo_envase = tk.Toplevel()
    ventana_ultimo_envase.title("Último Envase de Medicaciones")
    ventana_ultimo_envase.geometry("900x600")  # Ventana más grande
    ventana_ultimo_envase.configure(bg="#50C878")

    # Frame para el contenedor
    frame_contenedor = tk.Frame(ventana_ultimo_envase, bg="#50C878")
    frame_contenedor.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Título de la ventana
    tk.Label(frame_contenedor, text="Último Envase de Medicaciones", font=("Arial", 14, "bold"), bg="#50C878", fg="white").pack(pady=10)

    # Treeview para mostrar pacientes y medicaciones
    tree = ttk.Treeview(frame_contenedor, columns=("Paciente", "Medicamento", "Último Envase"), show="headings")
    tree.pack(fill=tk.BOTH, expand=True)

    # Configuración de las columnas
    tree.heading("Paciente", text="Paciente")
    tree.heading("Medicamento", text="Medicamento")
    tree.heading("Último Envase", text="Último Envase")
    
    tree.column("Paciente", width=200, anchor="center")
    tree.column("Medicamento", width=300, anchor="center")
    tree.column("Último Envase", width=200, anchor="center")

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

    # Consultar todos los pacientes y sus medicaciones
    conn = sqlite3.connect("pacientes.db")
    cursor = conn.cursor()

    query = """
        SELECT p.id, p.nombre, p.apellidos, m.medicacion, m.fecha_inicio, m.fecha_fin, m.posologia, m.unidades_por_caja
        FROM Pacientes p
        INNER JOIN Medicaciones m ON p.id = m.paciente_id
        ORDER BY p.apellidos ASC
    """
    cursor.execute(query)
    pacientes_medicaciones = cursor.fetchall()
    conn.close()

    # Procesar los resultados y calcular el último envase para cada medicación
    for paciente in pacientes_medicaciones:
        paciente_id, nombre, apellidos, medicacion, fecha_inicio, fecha_fin, posologia, unidades_por_caja = paciente
        
        # Calcular la frecuencia de reposición (en días) con base en la posología
        frecuencia_dias = max(1, unidades_por_caja // posologia)

        # Convertir las fechas de inicio y fin
        inicio = datetime.strptime(fecha_inicio, "%d-%m-%Y")
        fin = datetime.strptime(fecha_fin, "%d-%m-%Y")

        # Calcular el último envase
        fecha_actual = inicio
        while fecha_actual <= fin:
            if fecha_actual + timedelta(days=frecuencia_dias) > fin:  # Último envase
                # Insertar los datos en el Treeview
                tree.insert(
                    "",
                    "end",
                    values=(f"{nombre} {apellidos}",
                            f"{medicacion}",
                            f"{fecha_actual.strftime('%d-%m-%Y')}")
                )
            fecha_actual += timedelta(days=frecuencia_dias)

    # Botones para exportar e imprimir
    tk.Button(frame_contenedor, text="Imprimir", command=lambda: imprimir_ultimo_envase(tree, ventana_ultimo_envase), bg="#FF5733", fg="white", font=("Arial", 12)).pack(pady=10)
    tk.Button(frame_contenedor, text="Exportar a Excel", command=lambda: exportar_a_excel_local(tree), bg="#007C5C", fg="white", font=("Arial", 12)).pack(pady=10)

    # Botón para cerrar la ventana de último envase
    boton_cerrar = tk.Button(
        frame_contenedor,
        text="Cerrar",
        command=ventana_ultimo_envase.destroy,
        bg="#007C5C",
        fg="white",
        font=("Arial", 12)
    )
    boton_cerrar.pack(pady=10)

    ventana_ultimo_envase.mainloop()

# Configuración principal
from tkcalendar import Calendar
import sqlite3
import pandas as pd
from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import matplotlib.pyplot as plt



# Función para obtener estadísticas filtradas
def obtener_estadisticas_anuas(filtro, valor_filtro=None):
    """
    Función para obtener estadísticas anuales de medicación, filtrando por paciente, código nacional o nombre de medicación.
    
    Parámetros:
    - filtro: puede ser "paciente", "cn", o "medicacion"
    - valor_filtro: el valor por el cual filtrar (ejemplo, nombre de paciente o nombre de medicación)
    
    Retorna:
    - DataFrame con las estadísticas solicitadas.
    """
    # Establecer la conexión a la base de datos
    conn = sqlite3.connect("pacientes.db")
    cursor = conn.cursor()

    # Consulta SQL base
    query = """
        SELECT p.nombre, m.medicacion, m.cn, m.fecha_inicio, m.fecha_fin, m.posologia, m.unidades_por_caja
        FROM Medicaciones m
        INNER JOIN Pacientes p ON p.id = m.paciente_id
    """
    
    # Filtrar según el tipo de filtro proporcionado
    if filtro == "paciente":
        query += " WHERE p.nombre = ?"
        cursor.execute(query, (valor_filtro,))
    elif filtro == "cn":
        query += " WHERE m.cn = ?"
        cursor.execute(query, (valor_filtro,))
    elif filtro == "medicacion":
        query += " WHERE m.medicacion = ?"
        cursor.execute(query, (valor_filtro,))
    else:
        cursor.execute(query)

    # Obtener los resultados
    medicaciones = cursor.fetchall()
    conn.close()

    # Verifica si la consulta devolvió resultados
    if not medicaciones:
        messagebox.showinfo("Sin datos", "No se encontraron resultados para los filtros aplicados.")
        return pd.DataFrame()  # Si no hay datos, devuelve un DataFrame vacío

    # Crear una lista para almacenar los datos procesados
    datos = []

    for medicacion in medicaciones:
        nombre_paciente, nombre_medicacion, cn, fecha_inicio, fecha_fin, posologia, unidades_por_caja = medicacion

        # Parsear las fechas de inicio y fin
        inicio = datetime.strptime(fecha_inicio, "%d-%m-%Y")
        fin = datetime.strptime(fecha_fin, "%d-%m-%Y")

        # Calcular el número de días cubiertos por una caja
        dias_cubiertos = max(1, unidades_por_caja // posologia)

        # Iterar sobre el rango de fechas y agregar a la lista
        actual = inicio
        while actual <= fin:
            # Obtener el año de la fecha actual
            año = actual.year

            # Calcular la cantidad de cajas pautadas (cajas = unidades / unidades_por_caja)
            cantidad_pautada = unidades_por_caja / unidades_por_caja  # Aquí ya se está usando la cantidad de cajas

            # Añadir los datos a la lista
            datos.append([nombre_paciente, nombre_medicacion, cn, año, cantidad_pautada])

            # Incrementar la fecha en base a la posología (cada "dias_cubiertos")
            actual += timedelta(days=dias_cubiertos)

    # Convertir los datos a un DataFrame de pandas para un análisis más fácil
    df = pd.DataFrame(datos, columns=["Paciente", "Medicacion", "CN", "Año", "Cantidad Pautada"])

    # Asegurarse de que la columna 'Cantidad Pautada' contiene solo datos numéricos
    df["Cantidad Pautada"] = pd.to_numeric(df["Cantidad Pautada"], errors="coerce").fillna(0)

    # Agrupar por paciente, medicación, año, y sumar las cantidades pautadas
    df_agrupado = df.groupby(["Paciente", "Medicacion", "CN", "Año"]).agg({"Cantidad Pautada": "sum"}).reset_index()

    return df_agrupado

# Función para mostrar las estadísticas en una ventana
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import win32print  # Para manejo de impresoras en Windows
def mostrar_estadisticas(filtro, valor_filtro):
    """
    Muestra las estadísticas de medicación con opciones de exportar e imprimir directamente a una impresora.
    """
    # Llamar a la función de estadísticas y obtener los resultados
    if filtro == "paciente":
        # Si el filtro es por paciente, buscamos las estadísticas por el ID del paciente
        estadisticas = obtener_estadisticas_anuas("id", valor_filtro)
    else:
        # Si el filtro es por medicación o CN, continuamos como estaba
        estadisticas = obtener_estadisticas_anuas(filtro, valor_filtro)

    # Si no hay datos, no continuamos
    if estadisticas.empty:
        messagebox.showinfo("Sin datos", "No se encontraron datos para los filtros seleccionados.")
        return

    # Crear una ventana emergente para mostrar las estadísticas
    ventana_estadisticas = Toplevel()
    ventana_estadisticas.title("Estadísticas de Medicación")
    ventana_estadisticas.geometry("900x600")
    ventana_estadisticas.configure(bg="#50C878")

    # Mostrar las estadísticas en un widget Treeview
    frame_contenedor = Frame(ventana_estadisticas, bg="#50C878")
    frame_contenedor.pack(fill=BOTH, expand=True, padx=10, pady=10)

    tree = ttk.Treeview(frame_contenedor, columns=("Paciente", "Medicacion", "CN", "Año", "Cantidad Pautada"), show="headings")
    tree.pack(fill=BOTH, expand=True)

    # Configuración de las columnas
    tree.heading("Paciente", text="Paciente")
    tree.heading("Medicacion", text="Medicacion")
    tree.heading("CN", text="Código Nacional")
    tree.heading("Año", text="Año")
    tree.heading("Cantidad Pautada", text="Cantidad Pautada")

    tree.column("Paciente", width=200, anchor="center")
    tree.column("Medicacion", width=300, anchor="center")
    tree.column("CN", width=150, anchor="center")
    tree.column("Año", width=100, anchor="center")
    tree.column("Cantidad Pautada", width=150, anchor="center")

    # Insertar las estadísticas en el Treeview
    for _, row in estadisticas.iterrows():
        tree.insert("", "end", values=(row["Paciente"], row["Medicacion"], row["CN"], row["Año"], row["Cantidad Pautada"]))

    # Función para imprimir directamente
    def imprimir_estadisticas():
        try:
            # Crear ventana emergente para seleccionar impresora
            ventana_impresora = Toplevel(ventana_estadisticas)
            ventana_impresora.title("Seleccionar Impresora")
            ventana_impresora.geometry("400x200")
            ventana_impresora.configure(bg="#50C878")

            tk.Label(ventana_impresora, text="Selecciona una impresora:", bg="#50C878", font=("Arial", 12)).pack(pady=10)

            # Obtener lista de impresoras
            impresoras = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
            lista_impresoras = [impresora[2] for impresora in impresoras]

            # Crear combobox para seleccionar la impresora
            seleccion_impresora = StringVar()
            combobox_impresoras = ttk.Combobox(ventana_impresora, textvariable=seleccion_impresora, values=lista_impresoras, state="readonly", width=50)
            combobox_impresoras.pack(pady=10)
            combobox_impresoras.current(0)  # Seleccionar la primera impresora por defecto

            def enviar_a_impresora():
                try:
                    seleccion = seleccion_impresora.get()
                    if seleccion:
                        # Obtener datos del Treeview
                        texto_a_imprimir = "Estadísticas de Medicación:\n\n"
                        columnas = ["Paciente", "Medicacion", "CN", "Año", "Cantidad Pautada"]
                        texto_a_imprimir += "\t".join(columnas) + "\n"
                        texto_a_imprimir += "-" * 70 + "\n"

                        for child in tree.get_children():
                            fila = tree.item(child)["values"]
                            texto_a_imprimir += "\t".join(map(str, fila)) + "\n"

                        # Enviar el texto a la impresora seleccionada
                        handle_impresora = win32print.OpenPrinter(seleccion)
                        job = win32print.StartDocPrinter(handle_impresora, 1, ("Estadísticas de Medicación", None, "RAW"))
                        win32print.StartPagePrinter(handle_impresora)
                        win32print.WritePrinter(handle_impresora, texto_a_imprimir.encode("utf-8"))
                        win32print.EndPagePrinter(handle_impresora)
                        win32print.EndDocPrinter(handle_impresora)
                        win32print.ClosePrinter(handle_impresora)

                        messagebox.showinfo("Éxito", f"Estadísticas enviadas a la impresora: {seleccion}")
                        ventana_impresora.destroy()
                    else:
                        messagebox.showwarning("Advertencia", "No se seleccionó ninguna impresora.")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo imprimir: {e}")

            # Botón para confirmar la impresión
            Button(ventana_impresora, text="Imprimir", command=enviar_a_impresora, bg="#007C5C", fg="white", font=("Arial", 12)).pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el selector de impresoras: {e}")

    # Botón para imprimir
    Button(frame_contenedor, text="Imprimir", command=imprimir_estadisticas, bg="#FF5733", fg="white", font=("Arial", 12)).pack(pady=10)

    # Botón para exportar a Excel
    def exportar_a_excel_local():
        try:
            archivo = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                   filetypes=[("Excel Files", "*.xlsx")])
            if archivo:
                estadisticas.to_excel(archivo, index=False, engine="openpyxl")
                messagebox.showinfo("Éxito", f"Archivo exportado correctamente a {archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar a Excel: {e}")

    Button(frame_contenedor, text="Exportar a Excel", command=exportar_a_excel_local, bg="#007C5C", fg="white", font=("Arial", 12)).pack(pady=10)

    ventana_estadisticas.mainloop()

# Función para generar gráficos de las estadísticas
def generar_grafico(df):
    """
    Genera un gráfico de barras de las estadísticas anuales por medicación.
    """
    if df.empty:
        messagebox.showwarning("Sin datos", "No hay datos suficientes para generar el gráfico.")
        return

    try:
        # Agrupar por Medicación y Año para visualizar los totales de unidades pautadas
        df_grafico = df.groupby(["Medicacion", "Año"])["Cantidad Pautada"].sum().unstack()

        # Crear el gráfico
        df_grafico.plot(kind="bar", stacked=True, figsize=(10, 6))
        plt.title("Cantidad Pautada de Medicación por Año")
        plt.ylabel("Cantidad Pautada")
        plt.xlabel("Medicaciones")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el gráfico: {e}")

# Pantalla para elegir un filtro antes de mostrar las estadísticas
import sqlite3
from tkinter import messagebox, Toplevel, Label, Button, Entry, OptionMenu, StringVar, Listbox, Frame, BOTH, END, ACTIVE

def pantalla_filtro_estadisticas():
    """
    Pantalla para elegir un filtro antes de mostrar las estadísticas.
    """
    global paciente_id  # Variable global para almacenar el ID del paciente seleccionado

    # Inicializamos la variable paciente_id
    paciente_id = None

    # Crear la ventana de filtros
    ventana_filtro = Toplevel()
    ventana_filtro.title("Seleccionar Filtro para Estadísticas")
    ventana_filtro.geometry("800x600")
    ventana_filtro.configure(bg="#50C878")

    # Crear un Frame contenedor para mejorar la disposición
    frame_contenedor = Frame(ventana_filtro, bg="#50C878")
    frame_contenedor.pack(fill=BOTH, expand=True, padx=20, pady=20)

    # Título de la ventana
    titulo = Label(frame_contenedor, text="Seleccione un filtro para las estadísticas", bg="#50C878", fg="white", font=("Arial", 16, "bold"))
    titulo.pack(pady=20)

    # Instrucción de selección de filtro
    Label(frame_contenedor, text="Seleccione un filtro:", bg="#50C878", fg="white", font=("Arial", 12)).pack(pady=10)

    # Filtro de opción con estilo
    filtro_var = StringVar(ventana_filtro)
    filtro_var.set("paciente")  # Valor predeterminado
    filtros = ["paciente", "medicacion", "cn"]

    # Personalización del OptionMenu para que se vea más atractivo
    filtro_menu = OptionMenu(frame_contenedor, filtro_var, *filtros)
    filtro_menu.config(font=("Arial", 12), bg="#007C5C", fg="white", width=15)
    filtro_menu.pack(pady=10)

    # Instrucción para el valor del filtro
    Label(frame_contenedor, text="Ingrese el valor del filtro:", bg="#50C878", fg="white", font=("Arial", 12)).pack(pady=5)

    # Entrada para el valor del filtro
    entry_filtro = Entry(frame_contenedor, font=("Arial", 12), width=20)
    entry_filtro.pack(pady=10)

    # Listbox para mostrar las sugerencias
    lista_sugerencias = Listbox(frame_contenedor, width=40, height=10)
    lista_sugerencias.pack(pady=10)

    # Función para buscar pacientes y autocompletar
    def buscar_paciente_autocompletar(entry_busqueda, lista_sugerencias):
        def actualizar_lista():
            texto = entry_busqueda.get().strip().lower()
            lista_sugerencias.delete(0, END)

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

                if not resultados:
                    lista_sugerencias.insert(END, "No se encontraron resultados")
                    return

                for resultado in resultados:
                    lista_sugerencias.insert(END, f"{resultado[1]} {resultado[2]} - ID: {resultado[0]}")

            except sqlite3.Error as e:
                messagebox.showerror("Error de base de datos", f"No se pudo realizar la búsqueda: {e}")

        def seleccionar_paciente(event):
            global paciente_id  # Usamos la variable global para almacenar el ID del paciente
            if lista_sugerencias.curselection():
                texto_seleccionado = lista_sugerencias.get(ACTIVE)
                if texto_seleccionado == "No se encontraron resultados":
                    return

                # Extraer el ID del paciente desde el texto seleccionado
                paciente_id = int(texto_seleccionado.split("- ID: ")[1])  # Extrae el ID de la sugerencia
                nombre_completo = texto_seleccionado.split(" - ID: ")[0]  # Solo el nombre completo

                # Autocompletar el Entry con el nombre completo
                entry_busqueda.delete(0, END)
                entry_busqueda.insert(0, nombre_completo)  # Solo el nombre y apellidos

        lista_sugerencias.bind("<Double-1>", seleccionar_paciente)
        entry_busqueda.bind("<KeyRelease>", lambda _: actualizar_lista())

    # Llamamos a la función para habilitar la búsqueda de pacientes en la entrada
    buscar_paciente_autocompletar(entry_filtro, lista_sugerencias)

    # Función para cargar las estadísticas
    def cargar_estadisticas():
        filtro = filtro_var.get()
        valor_filtro = entry_filtro.get()  # Tomar el valor del filtro (nombre del paciente, medicación o CN)

        # Si es paciente, usaremos el ID del paciente guardado
        if filtro == "paciente" and paciente_id is not None:
            valor_filtro = paciente_id  # Usar el ID del paciente seleccionado

        ventana_filtro.destroy()  # Cerrar la ventana de filtros
        mostrar_estadisticas(filtro, valor_filtro)  # Mostrar las estadísticas con el filtro seleccionado

    # Botón para cargar las estadísticas con estilo
    button_cargar = Button(frame_contenedor, text="Mostrar Estadísticas", command=cargar_estadisticas, bg="#FF5733", fg="white", font=("Arial", 14, "bold"))
    button_cargar.pack(pady=20, padx=10)

    # Botón para cerrar la ventana de filtros
    button_cerrar = Button(frame_contenedor, text="Cancelar", command=ventana_filtro.destroy, bg="#E74C3C", fg="white", font=("Arial", 12, "bold"))
    button_cerrar.pack(pady=10)

    # Mostrar la ventana emergente
    ventana_filtro.mainloop()


def proxima_dispensacion():
    """
    Pantalla para buscar a un paciente y mostrar sus medicaciones y próximas fechas de reaprovisionamiento,
    calculando correctamente el intervalo de días actualizado.
    """
    # Crear la ventana
    ventana_dispensacion = Toplevel()
    ventana_dispensacion.title("Próxima Dispensación")
    ventana_dispensacion.geometry("1024x768")
    ventana_dispensacion.configure(bg="#50C878")

    # Título de la ventana
    Label(
        ventana_dispensacion,
        text="Buscar al Paciente",
        font=("Arial", 16, "bold"),
        bg="#50C878",
        fg="white"
    ).pack(pady=10)

    # Entrada para buscar pacientes
    frame_busqueda = Frame(ventana_dispensacion, bg="#50C878")
    frame_busqueda.pack(pady=10)

    entry_busqueda = Entry(frame_busqueda, font=("Arial", 12))
    entry_busqueda.pack(side="left", padx=5)

    # Lista de sugerencias
    lista_sugerencias = Listbox(ventana_dispensacion, height=10, width=50, font=("Arial", 12))
    lista_sugerencias.pack(pady=10)

    # Vincular el evento de búsqueda
    def buscar_paciente():
        lista_sugerencias.delete(0, END)  # Limpiar la lista

        # Obtener el texto ingresado
        texto = entry_busqueda.get()

        # Buscar pacientes en la base de datos
        conn = sqlite3.connect("pacientes.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, apellidos FROM Pacientes WHERE nombre LIKE ?", (f"%{texto}%",))
        pacientes = cursor.fetchall()
        conn.close()

        # Mostrar resultados en la lista
        for paciente in pacientes:
            lista_sugerencias.insert(END, f"{paciente[1]} {paciente[2]} - ID: {paciente[0]}")

    entry_busqueda.bind("<KeyRelease>", lambda event: buscar_paciente())

    # Frame para mostrar las medicaciones del paciente seleccionado
    frame_medicaciones = Frame(ventana_dispensacion, bg="#50C878")
    frame_medicaciones.pack(fill=BOTH, expand=True, padx=10, pady=10)

    medicaciones_listbox = Listbox(frame_medicaciones, height=15, width=80, font=("Arial", 12))
    medicaciones_listbox.pack(fill=BOTH, expand=True, padx=10, pady=10)

    # Función para mostrar las medicaciones y próximas fechas de reaprovisionamiento
    def mostrar_medicaciones(event):
        medicaciones_listbox.delete(0, END)  # Limpiar la lista de medicaciones

        # Obtener el paciente seleccionado
        seleccion = lista_sugerencias.curselection()
        if not seleccion:
            return
        paciente_info = lista_sugerencias.get(seleccion[0])
        paciente_id = int(paciente_info.split("- ID: ")[1])

        # Consultar medicaciones del paciente
        conn = sqlite3.connect("pacientes.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT medicacion, fecha_inicio, fecha_fin, posologia, unidades_por_caja, intervalo_dias
            FROM Medicaciones
            WHERE paciente_id = ?
        """, (paciente_id,))
        medicaciones = cursor.fetchall()
        conn.close()

        # Procesar cada medicación
        for medicacion in medicaciones:
            nombre_medicacion, fecha_inicio, fecha_fin, posologia, unidades_por_caja, intervalo_dias = medicacion

            # Calcular la frecuencia de reposición utilizando la fórmula:
            dias_cubiertos = max(1, unidades_por_caja // posologia)
            intervalo_calculado = (dias_cubiertos * intervalo_dias)  # Ajustamos el cálculo del intervalo

            inicio = datetime.strptime(fecha_inicio, "%d-%m-%Y")
            fin = datetime.strptime(fecha_fin, "%d-%m-%Y")
            fechas_reaprovisionamiento = []

            # Calcular fechas de reaprovisionamiento utilizando el intervalo calculado
            actual = inicio
            while actual <= fin:
                fechas_reaprovisionamiento.append(actual.strftime("%d-%m-%Y"))
                actual += timedelta(days=intervalo_calculado)

            # Verificar si es la última dispensación
            ultima_dispensacion = fin + timedelta(days=intervalo_calculado)
            hoy = datetime.now()

            mensaje_extra = ""
            if ultima_dispensacion.date() <= hoy.date():
                mensaje_extra = " - ¡Última Dispensación!"

            # Mostrar las fechas en la lista
            medicaciones_listbox.insert(END, f"Medicamento: {nombre_medicacion}")
            medicaciones_listbox.insert(END, f"Fechas de reaprovisionamiento: {', '.join(fechas_reaprovisionamiento)} {mensaje_extra}")
            medicaciones_listbox.insert(END, "-" * 50)  # Línea separadora

    # Vincular clic a la lista de sugerencias
    lista_sugerencias.bind("<Double-1>", mostrar_medicaciones)

    # Función para exportar a Excel
    def exportar_a_excel():
        try:
            # Recopilar datos
            medicaciones = []
            for i in range(medicaciones_listbox.size()):
                medicaciones.append(medicaciones_listbox.get(i))

            # Crear un DataFrame de pandas
            df = pd.DataFrame(medicaciones, columns=["Medicamentos y Fechas"])

            # Guardar en un archivo Excel
            archivo = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
            if archivo:
                df.to_excel(archivo, index=False)
                messagebox.showinfo("Éxito", f"Archivo exportado correctamente a {archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar a Excel: {e}")

    # Función para imprimir
    def imprimir_estadisticas():
        try:
            texto_a_imprimir = "Próxima Dispensación:\n\n"

            # Recopilar los datos de las medicaciones y fechas
            for i in range(medicaciones_listbox.size()):
                texto_a_imprimir += medicaciones_listbox.get(i) + "\n"

            # Crear ventana para elegir la impresora
            ventana_impresora = Toplevel(ventana_dispensacion)
            ventana_impresora.title("Seleccionar Impresora")
            ventana_impresora.geometry("400x200")
            ventana_impresora.configure(bg="#50C878")

            tk.Label(ventana_impresora, text="Selecciona una impresora:", bg="#50C878", font=("Arial", 12)).pack(pady=10)

            # Obtener lista de impresoras
            impresoras = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
            lista_impresoras = [impresora[2] for impresora in impresoras]

            # Crear combobox para seleccionar la impresora
            seleccion_impresora = StringVar()
            combobox_impresoras = ttk.Combobox(ventana_impresora, textvariable=seleccion_impresora, values=lista_impresoras, state="readonly", width=50)
            combobox_impresoras.pack(pady=10)
            combobox_impresoras.current(0)  # Seleccionar la primera impresora por defecto

            def enviar_a_impresora():
                try:
                    seleccion = seleccion_impresora.get()
                    if seleccion:
                        # Enviar el texto a la impresora seleccionada
                        handle_impresora = win32print.OpenPrinter(seleccion)
                        job = win32print.StartDocPrinter(handle_impresora, 1, ("Próxima Dispensación", None, "RAW"))
                        win32print.StartPagePrinter(handle_impresora)
                        win32print.WritePrinter(handle_impresora, texto_a_imprimir.encode("utf-8"))
                        win32print.EndPagePrinter(handle_impresora)
                        win32print.EndDocPrinter(handle_impresora)
                        win32print.ClosePrinter(handle_impresora)

                        messagebox.showinfo("Éxito", f"Estadísticas enviadas a la impresora: {seleccion}")
                        ventana_impresora.destroy()
                    else:
                        messagebox.showwarning("Advertencia", "No se seleccionó ninguna impresora.")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo imprimir: {e}")

            # Botón para confirmar la impresión
            Button(ventana_impresora, text="Imprimir", command=enviar_a_impresora, bg="#007C5C", fg="white", font=("Arial", 12)).pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el selector de impresoras: {e}")

    # Botones para exportar e imprimir
    Button(ventana_dispensacion, text="Exportar a Excel", command=exportar_a_excel, bg="#007C5C", fg="white", font=("Arial", 12)).pack(pady=10)
    Button(ventana_dispensacion, text="Imprimir", command=imprimir_estadisticas, bg="#FF5733", fg="white", font=("Arial", 12)).pack(pady=10)

    # Botón para cerrar la ventana
    Button(
        ventana_dispensacion,
        text="Cerrar",
        command=ventana_dispensacion.destroy,
        bg="#E74C3C",
        fg="white",
        font=("Arial", 12)
    ).pack(pady=10)

    ventana_dispensacion.mainloop()




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

    # Frame para los botones con diseño de tabla
    frame_botones = Frame(frame_contenedor, bg="#50C878")
    frame_botones.pack(fill=BOTH, expand=True, padx=10, pady=20)

    # Lista de botones y sus comandos
    botones = [
        ("Añadir Paciente", lambda: añadir_paciente(root, calendar)),
        ("Ver Todos los Pacientes", ver_todos_pacientes),
        ("Exportar a CSV o Excel", exportar_datos),
        ("Copia de Seguridad", backup_database),
        ("Avisar al Paciente por Whatsapp", abrir_ventana_aviso_paciente),
        ("Mostrar Último Envase", mostrar_ultimo_envase),
        ("Mostrar Estadísticas", pantalla_filtro_estadisticas),
        ("Próxima Dispensación", proxima_dispensacion),
        ("Refrescar Calendario", lambda: marcar_dias_medicacion(calendar)),
    ]

    # Colocar botones en una cuadrícula
    for i, (texto, comando) in enumerate(botones):
        Button(
            frame_botones,
            text=texto,
            command=comando,
            bg="#007C5C" if "Refrescar" not in texto else "#FF5733",
            fg="white",
            font=("Arial", 12),
            width=25
        ).grid(row=i // 2, column=i % 2, padx=10, pady=10, sticky="nsew")

    # Configurar columnas para que se ajusten uniformemente
    frame_botones.grid_columnconfigure(0, weight=1)
    frame_botones.grid_columnconfigure(1, weight=1)

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
