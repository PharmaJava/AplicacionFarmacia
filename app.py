import sqlite3
from tkinter import *
from tkinter import messagebox, ttk
from tkcalendar import Calendar
from datetime import datetime
import csv
import shutil
import os
import time


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
            fecha DATE NOT NULL,
            FOREIGN KEY (paciente_id) REFERENCES Pacientes (id)
        )
    """)
    conn.commit()
    conn.close()

# Añadir paciente y múltiples medicaciones

def añadir_paciente(root, calendar):
    def guardar_paciente():
        nombre = entry_nombre.get()
        apellidos = entry_apellidos.get()
        telefono = entry_telefono.get()
        numero_tarjeta = entry_tarjeta.get()

        if not nombre or not apellidos:
            messagebox.showwarning("Datos incompletos", "El nombre y los apellidos son obligatorios.")
            return

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
            cursor.execute("""
                INSERT INTO Medicaciones (paciente_id, medicacion, cn, fecha)
                VALUES (?, ?, ?, ?)
            """, (paciente_id, medicacion["medicamento"], medicacion["cn"], medicacion["fecha"]))

        conn.commit()
        conn.close()

        # Refrescar el calendario
        marcar_dias_medicacion(calendar)

        messagebox.showinfo("Éxito", "Paciente y medicaciones guardados correctamente.")
        ventana.destroy()

    def añadir_medicacion():
        def guardar_medicacion():
            medicamento = entry_medicamento.get()
            cn = entry_cn.get()
            fecha = calendar_medicacion.get_date()

            if not medicamento or not fecha:
                messagebox.showwarning("Datos incompletos", "Debe ingresar un medicamento y seleccionar una fecha.")
                return

            medicaciones.append({"medicamento": medicamento, "cn": cn, "fecha": fecha})
            lista_medicaciones.insert(END, f"{medicamento} (CN: {cn}) - {fecha}")
            ventana_medicacion.destroy()

        # Ventana para añadir medicación
        ventana_medicacion = Toplevel()
        ventana_medicacion.title("Añadir Medicación")
        ventana_medicacion.configure(bg="#50C878")

        Label(ventana_medicacion, text="Medicamento:", bg="#50C878").grid(row=0, column=0, padx=5, pady=5)
        entry_medicamento = Entry(ventana_medicacion)
        entry_medicamento.grid(row=0, column=1, padx=5, pady=5)

        Label(ventana_medicacion, text="CN (opcional):", bg="#50C878").grid(row=1, column=0, padx=5, pady=5)
        entry_cn = Entry(ventana_medicacion)
        entry_cn.grid(row=1, column=1, padx=5, pady=5)

        calendar_medicacion = Calendar(ventana_medicacion, selectmode="day", date_pattern="dd-mm-yyyy", background="#50C878", foreground="white")
        calendar_medicacion.grid(row=2, column=0, columnspan=2, pady=10)

        Button(ventana_medicacion, text="Guardar Medicación", command=guardar_medicacion, bg="#007C5C", fg="white").grid(row=3, column=0, columnspan=2, pady=10)

    def eliminar_medicacion():
        # Obtener el índice de la medicación seleccionada
        seleccion = lista_medicaciones.curselection()
        if not seleccion:
            messagebox.showwarning("Seleccionar medicación", "Debe seleccionar una medicación para eliminar.")
            return

        index = seleccion[0]
        # Eliminar la medicación de la lista temporal
        del medicaciones[index]
        # Eliminarla visualmente de la Listbox
        lista_medicaciones.delete(index)

    # Ventana para añadir paciente
    ventana = Toplevel(root)
    ventana.title("Añadir Paciente")
    ventana.configure(bg="#50C878")

    medicaciones = []  # Lista para almacenar medicaciones temporalmente

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

# Función para marcar los días con medicaciones en el calendario
def marcar_dias_medicacion(calendar):
    conn = sqlite3.connect("pacientes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT fecha FROM Medicaciones")
    fechas = cursor.fetchall()
    conn.close()

    for fecha in fechas:
        try:
            # Convertir la fecha de la base de datos a formato datetime
            calendar.calevent_create(datetime.strptime(fecha[0], "%d-%m-%Y"), "Medicaciones", "med")
        except ValueError:
            pass

    # Configurar apariencia de las fechas con medicaciones
    calendar.tag_config("med", background="red", foreground="white")



    def agregar_medicacion():
        row = len(medicacion_entries) + 5  # Iniciar en la fila 5 y aumentar por cada nueva medicación
        Label(ventana_paciente, text="Medicamento", bg="#50C878").grid(row=row, column=0, padx=5, pady=5)
        medicacion_entry = Entry(ventana_paciente)
        medicacion_entry.grid(row=row, column=1, padx=5, pady=5)
        medicacion_entries.append(medicacion_entry)

        Label(ventana_paciente, text="CN", bg="#50C878").grid(row=row+1, column=0, padx=5, pady=5)
        cn_entry = Entry(ventana_paciente)
        cn_entry.grid(row=row+1, column=1, padx=5, pady=5)
        cn_entries.append(cn_entry)

        Label(ventana_paciente, text="Fecha de Medicación", bg="#50C878").grid(row=row+2, column=0, padx=5, pady=5)
        fecha_entry = Calendar(ventana_paciente, selectmode="day", date_pattern="dd-mm-yyyy", background="#50C878", foreground="white")
        fecha_entry.grid(row=row+2, column=1, padx=5, pady=5)
        fecha_entries.append(fecha_entry)

    Button(ventana_paciente, text="Añadir Medicación", command=agregar_medicacion, bg="#007C5C", fg="white").grid(row=4, column=0, columnspan=2, pady=10)

    Button(ventana_paciente, text="Guardar", command=guardar_paciente, bg="#007C5C", fg="white").grid(row=999, column=0, columnspan=2, pady=10)

def editar_paciente_desde_lista(paciente_id):
    def guardar_cambios():
        nuevo_nombre = entry_nombre.get()
        nuevos_apellidos = entry_apellidos.get()
        nuevo_telefono = entry_telefono.get()
        nueva_tarjeta = entry_tarjeta.get()

        if not nuevo_nombre or not nuevos_apellidos:
            messagebox.showwarning("Datos incompletos", "El nombre y los apellidos son obligatorios.")
            return

        conn = sqlite3.connect("pacientes.db")
        cursor = conn.cursor()

        # Actualizar datos del paciente
        cursor.execute("""
            UPDATE Pacientes
            SET nombre = ?, apellidos = ?, telefono = ?, numero_tarjeta = ?
            WHERE id = ?
        """, (nuevo_nombre, nuevos_apellidos, nuevo_telefono, nueva_tarjeta, paciente_id))

        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Paciente actualizado correctamente.")
        ventana.destroy()

    conn = sqlite3.connect("pacientes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Pacientes WHERE id = ?", (paciente_id,))
    paciente = cursor.fetchone()
    conn.close()

    ventana = Toplevel()
    ventana.title("Editar Paciente")
    ventana.configure(bg="#50C878")

    Label(ventana, text="Nombre:", bg="#50C878").grid(row=0, column=0, padx=5, pady=5)
    entry_nombre = Entry(ventana)
    entry_nombre.grid(row=0, column=1, padx=5, pady=5)
    entry_nombre.insert(0, paciente[1])

    Label(ventana, text="Apellidos:", bg="#50C878").grid(row=1, column=0, padx=5, pady=5)
    entry_apellidos = Entry(ventana)
    entry_apellidos.grid(row=1, column=1, padx=5, pady=5)
    entry_apellidos.insert(0, paciente[2])

    Label(ventana, text="Teléfono:", bg="#50C878").grid(row=2, column=0, padx=5, pady=5)
    entry_telefono = Entry(ventana)
    entry_telefono.grid(row=2, column=1, padx=5, pady=5)
    entry_telefono.insert(0, paciente[3])

    Label(ventana, text="Número de Tarjeta:", bg="#50C878").grid(row=3, column=0, padx=5, pady=5)
    entry_tarjeta = Entry(ventana)
    entry_tarjeta.grid(row=3, column=1, padx=5, pady=5)
    entry_tarjeta.insert(0, paciente[4])

    Button(ventana, text="Guardar Cambios", command=guardar_cambios, bg="#007C5C", fg="white").grid(row=4, column=0, columnspan=2, pady=10)


# Función para marcar los días con medicaciones
def marcar_dias_medicacion(calendar):
    conn = sqlite3.connect("pacientes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT fecha FROM Medicaciones")
    fechas = cursor.fetchall()
    conn.close()

    for fecha in fechas:
        try:
            calendar.calevent_create(datetime.strptime(fecha[0], "%d-%m-%Y"), "Medicaciones", "med")
        except ValueError:
            pass

    calendar.tag_config("med", background="red", foreground="white")


# Función para ver medicaciones del día
def ver_medicacion_dia(fecha):
    conn = sqlite3.connect("pacientes.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Pacientes.nombre, Pacientes.apellidos, Medicaciones.medicacion, Medicaciones.cn
        FROM Medicaciones
        JOIN Pacientes ON Medicaciones.paciente_id = Pacientes.id
        WHERE Medicaciones.fecha = ?
    """, (fecha,))
    medicaciones = cursor.fetchall()
    conn.close()

    if medicaciones:
        texto = "\n".join([f"{nombre} {apellidos}: {medicacion} (CN: {cn})" for nombre, apellidos, medicacion, cn in medicaciones])
        messagebox.showinfo(f"Medicaciones del {fecha}", texto)
    else:
        messagebox.showinfo(f"Medicaciones del {fecha}", "No hay medicaciones programadas para este día.")


# Función para mostrar la información del paciente seleccionado
def mostrar_pacientes():
    def seleccionar_paciente(event):
        seleccion = lista_pacientes.curselection()
        if seleccion:
            indice = seleccion[0]
            paciente_id = ids_pacientes[indice]
            editar_paciente_desde_lista(paciente_id)

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
def mostrar_informacion_paciente(paciente_id):
    """
    Abre la ventana de edición del paciente seleccionado según su ID.
    """
    editar_paciente_desde_lista(paciente_id)


def buscar_paciente_autocompletar(entry_busqueda, lista_sugerencias):
    """
    Busca pacientes en tiempo real según el texto ingresado en el Entry
    y muestra resultados en la Listbox.
    """
    texto = entry_busqueda.get().lower()
    lista_sugerencias.delete(0, END)  # Limpiar sugerencias previas

    if texto.strip():  # Si el texto no está vacío
        conn = sqlite3.connect("pacientes.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nombre, apellidos FROM Pacientes
            WHERE LOWER(nombre || ' ' || apellidos) LIKE ?
        """, (f"%{texto}%",))
        resultados = cursor.fetchall()
        conn.close()

        # Agregar resultados a la Listbox
        for paciente in resultados:
            lista_sugerencias.insert(END, f"{paciente[1]} {paciente[2]} - ID: {paciente[0]}")

    # Evento para manejar la selección del paciente
    def seleccionar_paciente(event):
        if lista_sugerencias.curselection():  # Verificar si hay una selección
            texto_seleccionado = lista_sugerencias.get(ACTIVE)
            try:
                # Extraer el ID del texto seleccionado
                paciente_id = int(texto_seleccionado.split("- ID: ")[1])
                mostrar_informacion_paciente(paciente_id)
            except (IndexError, ValueError):
                messagebox.showerror("Error", "No se pudo obtener el ID del paciente.")

    # Vincular el evento a la Listbox
    lista_sugerencias.bind("<Double-1>", seleccionar_paciente)


# Función para mostrar todos los pacientes
def ver_todos_pacientes():
    ventana_todos = Toplevel()
    ventana_todos.title("Todos los Pacientes")
    ventana_todos.configure(bg="#50C878")

    tree = ttk.Treeview(ventana_todos, columns=("Nombre", "Apellidos", "Teléfono", "Tarjeta"), show="headings")
    tree.heading("Nombre", text="Nombre")
    tree.heading("Apellidos", text="Apellidos")
    tree.heading("Teléfono", text="Teléfono")
    tree.heading("Tarjeta", text="Tarjeta")
    tree.pack(fill=BOTH, expand=True)

    conn = sqlite3.connect("pacientes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Pacientes")
    pacientes = cursor.fetchall()
    conn.close()

    for paciente in pacientes:
        tree.insert("", END, values=(paciente[1], paciente[2], paciente[3], paciente[4]))

    def on_item_double_click(event):
        item = tree.selection()[0]
        paciente_id = tree.item(item, "values")[0]  # Aquí corregimos el ID
        mostrar_informacion_paciente(paciente_id)

    tree.bind("<Double-1>", on_item_double_click)

# Función para exportar datos a CSV
def exportar_datos():
    conn = sqlite3.connect("pacientes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Pacientes")
    pacientes = cursor.fetchall()
    conn.close()

    with open("pacientes.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Nombre", "Apellidos", "Teléfono", "Número Tarjeta"])
        for paciente in pacientes:
            writer.writerow(paciente)
    messagebox.showinfo("Éxito", "Datos exportados correctamente a pacientes.csv")

# Búsqueda dinámica
def buscar_paciente_autocompletar(entry, lista_sugerencias):
    query = entry.get()
    if not query:
        lista_sugerencias.delete(0, END)
        return

    conn = sqlite3.connect("pacientes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, apellidos FROM Pacientes WHERE nombre LIKE ?", (f"%{query}%",))
    resultados = cursor.fetchall()
    conn.close()

    lista_sugerencias.delete(0, END)
    for resultado in resultados:
        lista_sugerencias.insert(END, f"{resultado[1]} {resultado[2]} - ID: {resultado[0]}")

# Función para hacer backup de la base de datos
def backup_database():
    try:
        timestamp = time.strftime("%d%m%Y%H%M%S")
        backup_file = f"pacientes_backup_{timestamp}.db"
        shutil.copy("pacientes.db", backup_file)
        messagebox.showinfo("Backup realizado", f"Se ha creado un backup en {backup_file}")
    except Exception as e:
        messagebox.showerror("Error", f"Error al crear el backup: {e}")

# Modificar función para mostrar medicaciones en "Ver Todos los Pacientes"
def ver_todos_pacientes():
    def cargar_datos():
        # Limpiar tabla existente
        for row in tree.get_children():
            tree.delete(row)
        
        # Conectar a la base de datos y cargar datos
        conn = sqlite3.connect("pacientes.db")
        cursor = conn.cursor()
        
        # Obtener datos de los pacientes junto con la fecha de la última medicación
        cursor.execute("""
            SELECT 
                p.id, p.nombre, p.apellidos, p.telefono, p.numero_tarjeta,
                MAX(m.fecha) as ultima_fecha_medicacion
            FROM Pacientes p
            LEFT JOIN Medicaciones m ON p.id = m.paciente_id
            GROUP BY p.id
            ORDER BY p.apellidos, p.nombre
        """)
        pacientes = cursor.fetchall()
        conn.close()
        
        # Insertar datos en la tabla
        for paciente in pacientes:
            tree.insert("", "end", values=(
                paciente[0], paciente[1], paciente[2], paciente[3], 
                paciente[4], paciente[5] if paciente[5] else "Sin medicación"
            ))

    # Crear ventana
    ventana = Toplevel()
    ventana.title("Todos los Pacientes")
    ventana.configure(bg="#50C878")
    ventana.geometry("900x500")  # Aumentar tamaño para acomodar las columnas

    # Crear Treeview para mostrar datos
    columnas = ("ID", "Nombre", "Apellidos", "Teléfono", "Tarjeta", "Fecha")
    tree = ttk.Treeview(ventana, columns=columnas, show="headings", height=15)
    tree.pack(pady=10, fill="both", expand=True)

    # Definir encabezados y tamaños de columna
    tree.heading("ID", text="ID")
    tree.column("ID", width=50, anchor="center")
    tree.heading("Nombre", text="Nombre")
    tree.column("Nombre", width=150, anchor="center")
    tree.heading("Apellidos", text="Apellidos")
    tree.column("Apellidos", width=150, anchor="center")
    tree.heading("Teléfono", text="Teléfono")
    tree.column("Teléfono", width=100, anchor="center")
    tree.heading("Tarjeta", text="Tarjeta")
    tree.column("Tarjeta", width=100, anchor="center")
    tree.heading("Fecha", text="Fecha Medicación")
    tree.column("Fecha", width=150, anchor="center")

    # Botón para recargar los datos
    Button(ventana, text="Refrescar", command=cargar_datos, bg="#007C5C", fg="white").pack(pady=10)

    # Cargar datos inicialmente
    cargar_datos()

    ventana_todos = Toplevel()
    ventana_todos.title("Todos los Pacientes")
    ventana_todos.configure(bg="#50C878")

    tree = ttk.Treeview(ventana_todos, columns=("Nombre", "Apellidos", "Teléfono", "Medicaciones"), show="headings")
    tree.heading("Nombre", text="Nombre")
    tree.heading("Apellidos", text="Apellidos")
    tree.heading("Teléfono", text="Teléfono")
    tree.heading("Medicaciones", text="Medicaciones")
    tree.pack(fill=BOTH, expand=True)

    conn = sqlite3.connect("pacientes.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Pacientes.id, Pacientes.nombre, Pacientes.apellidos, Pacientes.telefono,
        GROUP_CONCAT(Medicaciones.medicacion, ', ') AS medicaciones
        FROM Pacientes
        LEFT JOIN Medicaciones ON Pacientes.id = Medicaciones.paciente_id
        GROUP BY Pacientes.id
    """)
    pacientes = cursor.fetchall()
    conn.close()

    for paciente in pacientes:
        tree.insert("", END, values=(paciente[1], paciente[2], paciente[3], paciente[4] or "Sin medicaciones"))

    def on_item_double_click(event):
        item = tree.selection()[0]
        paciente_id = tree.item(item, "values")[0]
        editar_paciente(paciente_id)

    tree.bind("<Double-1>", on_item_double_click)

# Función para editar datos del paciente

    def guardar_cambios():
        nuevo_nombre = entry_nombre.get()
        nuevos_apellidos = entry_apellidos.get()
        nuevo_telefono = entry_telefono.get()
        nuevo_numero_tarjeta = entry_tarjeta.get()
        nuevas_medicaciones = text_medicaciones.get("1.0", END).strip().split("\n")

        if not nuevo_nombre or not nuevos_apellidos:
            messagebox.showwarning("Datos incompletos", "El nombre y los apellidos son obligatorios.")
            return

        conn = sqlite3.connect("pacientes.db")
        cursor = conn.cursor()
        # Actualizar datos del paciente
        cursor.execute("""
            UPDATE Pacientes
            SET nombre = ?, apellidos = ?, telefono = ?, numero_tarjeta = ?
            WHERE id = ?
        """, (nuevo_nombre, nuevos_apellidos, nuevo_telefono, nuevo_numero_tarjeta, paciente_id))

        # Eliminar medicaciones existentes
        cursor.execute("DELETE FROM Medicaciones WHERE paciente_id = ?", (paciente_id,))

        # Añadir nuevas medicaciones
        for medicacion in nuevas_medicaciones:
            detalles = medicacion.split(";")
            if len(detalles) == 3:  # Medicamento;CN;Fecha
                medicamento, cn, fecha = detalles
                cursor.execute("""
                    INSERT INTO Medicaciones (paciente_id, medicacion, cn, fecha)
                    VALUES (?, ?, ?, ?)
                """, (paciente_id, medicamento.strip(), cn.strip(), fecha.strip()))

        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Datos del paciente y medicaciones actualizados correctamente.")
        ventana_editar.destroy()
        marcar_dias_medicacion(calendar)

    # Obtener datos del paciente
    conn = sqlite3.connect("pacientes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Pacientes WHERE id = ?", (paciente_id,))
    paciente = cursor.fetchone()

    cursor.execute("SELECT medicacion, cn, fecha FROM Medicaciones WHERE paciente_id = ?", (paciente_id,))
    medicaciones = cursor.fetchall()
    conn.close()

    ventana_editar = Toplevel()
    ventana_editar.title("Editar Paciente")
    ventana_editar.configure(bg="#50C878")

    # Campos de datos personales
    Label(ventana_editar, text="Nombre:", bg="#50C878").grid(row=0, column=0, padx=5, pady=5)
    entry_nombre = Entry(ventana_editar)
    entry_nombre.insert(0, paciente[1])
    entry_nombre.grid(row=0, column=1, padx=5, pady=5)

    Label(ventana_editar, text="Apellidos:", bg="#50C878").grid(row=1, column=0, padx=5, pady=5)
    entry_apellidos = Entry(ventana_editar)
    entry_apellidos.insert(0, paciente[2])
    entry_apellidos.grid(row=1, column=1, padx=5, pady=5)

    Label(ventana_editar, text="Teléfono:", bg="#50C878").grid(row=2, column=0, padx=5, pady=5)
    entry_telefono = Entry(ventana_editar)
    entry_telefono.insert(0, paciente[3])
    entry_telefono.grid(row=2, column=1, padx=5, pady=5)

    Label(ventana_editar, text="Número de Tarjeta:", bg="#50C878").grid(row=3, column=0, padx=5, pady=5)
    entry_tarjeta = Entry(ventana_editar)
    entry_tarjeta.insert(0, paciente[4])
    entry_tarjeta.grid(row=3, column=1, padx=5, pady=5)

    # Campo para medicaciones
    Label(ventana_editar, text="Medicaciones (Medicamento;CN;Fecha por línea):", bg="#50C878").grid(row=4, column=0, padx=5, pady=5)
    text_medicaciones = Text(ventana_editar, height=10, width=40)
    for medicacion in medicaciones:
        text_medicaciones.insert(END, f"{medicacion[0]};{medicacion[1]};{medicacion[2]}\n")
    text_medicaciones.grid(row=4, column=1, padx=5, pady=5)

    Button(ventana_editar, text="Guardar Cambios", command=guardar_cambios, bg="#007C5C", fg="white").grid(row=5, column=0, columnspan=2, pady=10)

    def guardar_cambios():
        nuevo_nombre = entry_nombre.get()
        nuevos_apellidos = entry_apellidos.get()
        nuevo_telefono = entry_telefono.get()
        nuevo_numero_tarjeta = entry_tarjeta.get()

        if not nuevo_nombre or not nuevos_apellidos:
            messagebox.showwarning("Datos incompletos", "El nombre y los apellidos son obligatorios.")
            return

        conn = sqlite3.connect("pacientes.db")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Pacientes
            SET nombre = ?, apellidos = ?, telefono = ?, numero_tarjeta = ?
            WHERE id = ?
        """, (nuevo_nombre, nuevos_apellidos, nuevo_telefono, nuevo_numero_tarjeta, paciente_id))
        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Datos del paciente actualizados correctamente.")
        ventana_editar.destroy()

    conn = sqlite3.connect("pacientes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Pacientes WHERE id = ?", (paciente_id,))
    paciente = cursor.fetchone()
    conn.close()

    ventana_editar = Toplevel()
    ventana_editar.title("Editar Paciente")
    ventana_editar.configure(bg="#50C878")

    Label(ventana_editar, text="Nombre:", bg="#50C878").grid(row=0, column=0, padx=5, pady=5)
    entry_nombre = Entry(ventana_editar)
    entry_nombre.insert(0, paciente[1])
    entry_nombre.grid(row=0, column=1, padx=5, pady=5)

    Label(ventana_editar, text="Apellidos:", bg="#50C878").grid(row=1, column=0, padx=5, pady=5)
    entry_apellidos = Entry(ventana_editar)
    entry_apellidos.insert(0, paciente[2])
    entry_apellidos.grid(row=1, column=1, padx=5, pady=5)

    Label(ventana_editar, text="Teléfono:", bg="#50C878").grid(row=2, column=0, padx=5, pady=5)
    entry_telefono = Entry(ventana_editar)
    entry_telefono.insert(0, paciente[3])
    entry_telefono.grid(row=2, column=1, padx=5, pady=5)

    Label(ventana_editar, text="Número de Tarjeta:", bg="#50C878").grid(row=3, column=0, padx=5, pady=5)
    entry_tarjeta = Entry(ventana_editar)
    entry_tarjeta.insert(0, paciente[4])
    entry_tarjeta.grid(row=3, column=1, padx=5, pady=5)

    Button(ventana_editar, text="Guardar Cambios", command=guardar_cambios, bg="#007C5C", fg="white").grid(row=4, column=0, columnspan=2, pady=10)
def editar_paciente_desde_lista(paciente_id):
    def guardar_cambios():
        nuevo_nombre = entry_nombre.get()
        nuevos_apellidos = entry_apellidos.get()
        nuevo_telefono = entry_telefono.get()
        nuevo_numero_tarjeta = entry_tarjeta.get()

        if not nuevo_nombre or not nuevos_apellidos:
            messagebox.showwarning("Datos incompletos", "El nombre y los apellidos son obligatorios.")
            return

        conn = sqlite3.connect("pacientes.db")
        cursor = conn.cursor()
        
        # Actualizar datos del paciente
        cursor.execute("""
            UPDATE Pacientes
            SET nombre = ?, apellidos = ?, telefono = ?, numero_tarjeta = ?
            WHERE id = ?
        """, (nuevo_nombre, nuevos_apellidos, nuevo_telefono, nuevo_numero_tarjeta, paciente_id))

        # Eliminar medicaciones existentes
        cursor.execute("DELETE FROM Medicaciones WHERE paciente_id = ?", (paciente_id,))

        # Guardar las nuevas medicaciones
        for medicacion in medicaciones:
            cursor.execute("""
                INSERT INTO Medicaciones (paciente_id, medicacion, cn, fecha)
                VALUES (?, ?, ?, ?)
            """, (paciente_id, medicacion["medicamento"], medicacion["cn"], medicacion["fecha"]))

        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Datos del paciente actualizados correctamente.")
        ventana_editar.destroy()

    def añadir_medicacion():
        def guardar_medicacion():
            medicamento = entry_medicamento.get()
            cn = entry_cn.get()
            fecha = calendar_medicacion.get_date()

            if not medicamento or not fecha:
                messagebox.showwarning("Datos incompletos", "Debe ingresar un medicamento y seleccionar una fecha.")
                return

            medicaciones.append({"medicamento": medicamento, "cn": cn, "fecha": fecha})
            lista_medicaciones.insert(END, f"{medicamento} (CN: {cn}) - {fecha}")
            ventana_medicacion.destroy()

        # Ventana para añadir medicación
        ventana_medicacion = Toplevel()
        ventana_medicacion.title("Añadir Medicación")
        ventana_medicacion.configure(bg="#50C878")

        Label(ventana_medicacion, text="Medicamento:", bg="#50C878").grid(row=0, column=0, padx=5, pady=5)
        entry_medicamento = Entry(ventana_medicacion)
        entry_medicamento.grid(row=0, column=1, padx=5, pady=5)

        Label(ventana_medicacion, text="CN (opcional):", bg="#50C878").grid(row=1, column=0, padx=5, pady=5)
        entry_cn = Entry(ventana_medicacion)
        entry_cn.grid(row=1, column=1, padx=5, pady=5)

        calendar_medicacion = Calendar(ventana_medicacion, selectmode="day", date_pattern="dd-mm-yyyy", background="#50C878", foreground="white")
        calendar_medicacion.grid(row=2, column=0, columnspan=2, pady=10)

        Button(ventana_medicacion, text="Guardar Medicación", command=guardar_medicacion, bg="#007C5C", fg="white").grid(row=3, column=0, columnspan=2, pady=10)

    def eliminar_medicacion():
        seleccion = lista_medicaciones.curselection()
        if not seleccion:
            messagebox.showwarning("Seleccionar medicación", "Debe seleccionar una medicación para eliminar.")
            return

        index = seleccion[0]
        del medicaciones[index]  # Eliminar de la lista temporal
        lista_medicaciones.delete(index)  # Eliminar del Listbox

    # Obtener datos del paciente desde la base de datos
    conn = sqlite3.connect("pacientes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Pacientes WHERE id = ?", (paciente_id,))
    paciente = cursor.fetchone()

    cursor.execute("SELECT medicacion, cn, fecha FROM Medicaciones WHERE paciente_id = ?", (paciente_id,))
    medicaciones_actuales = cursor.fetchall()
    conn.close()

    medicaciones = [{"medicamento": m[0], "cn": m[1], "fecha": m[2]} for m in medicaciones_actuales]

    # Ventana de edición
    ventana_editar = Toplevel()
    ventana_editar.title("Editar Paciente")
    ventana_editar.configure(bg="#50C878")

    Label(ventana_editar, text="Nombre:", bg="#50C878").grid(row=0, column=0, padx=5, pady=5)
    entry_nombre = Entry(ventana_editar)
    entry_nombre.insert(0, paciente[1])
    entry_nombre.grid(row=0, column=1, padx=5, pady=5)

    Label(ventana_editar, text="Apellidos:", bg="#50C878").grid(row=1, column=0, padx=5, pady=5)
    entry_apellidos = Entry(ventana_editar)
    entry_apellidos.insert(0, paciente[2])
    entry_apellidos.grid(row=1, column=1, padx=5, pady=5)

    Label(ventana_editar, text="Teléfono:", bg="#50C878").grid(row=2, column=0, padx=5, pady=5)
    entry_telefono = Entry(ventana_editar)
    entry_telefono.insert(0, paciente[3])
    entry_telefono.grid(row=2, column=1, padx=5, pady=5)

    Label(ventana_editar, text="Número de Tarjeta:", bg="#50C878").grid(row=3, column=0, padx=5, pady=5)
    entry_tarjeta = Entry(ventana_editar)
    entry_tarjeta.insert(0, paciente[4])
    entry_tarjeta.grid(row=3, column=1, padx=5, pady=5)

    Button(ventana_editar, text="Añadir Medicación", command=añadir_medicacion, bg="#007C5C", fg="white").grid(row=4, column=0, columnspan=2, pady=10)

    lista_medicaciones = Listbox(ventana_editar, height=10, width=50)
    lista_medicaciones.grid(row=5, column=0, columnspan=2, padx=5, pady=5)
    for medicacion in medicaciones:
        lista_medicaciones.insert(END, f"{medicacion['medicamento']} (CN: {medicacion['cn']}) - {medicacion['fecha']}")

    Button(ventana_editar, text="Eliminar Medicación", command=eliminar_medicacion, bg="#E74C3C", fg="white").grid(row=6, column=0, columnspan=2, pady=10)

    Button(ventana_editar, text="Guardar Cambios", command=guardar_cambios, bg="#007C5C", fg="white").grid(row=7, column=0, columnspan=2, pady=10)

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
    Button(root, text="Exportar a CSV", command=exportar_datos, bg="#007C5C", fg="white").pack(pady=5)
    Button(root, text="Hacer Backup", command=backup_database, bg="#007C5C", fg="white").pack(pady=5)

    # Búsqueda de pacientes
    frame_busqueda = Frame(root, bg="#50C878")
    frame_busqueda.pack(pady=10)

    # Entrada de búsqueda
    entry_busqueda = Entry(frame_busqueda)
    entry_busqueda.pack(side=LEFT, padx=5)

    # Botón de limpiar búsqueda
    Button(frame_busqueda, text="Limpiar", 
           command=lambda: (entry_busqueda.delete(0, END), lista_sugerencias.delete(0, END)),
           bg="#E74C3C", fg="white").pack(side=LEFT, padx=5)

    # Título para la lista de pacientes
    Label(root, text="Búsqueda de pacientes:", bg="#50C878", fg="white").pack(pady=(10, 5))

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

    root.mainloop()


# Inicializar base de datos y lanzar programa
if __name__ == "__main__":
    init_db()
    main()
