import sqlite3 as sql

class datos_guardados : 

    def __init__(self, producto, precio, cantidad, fecha, total):
        self.producto = producto
        self.precio = precio
        self.cantidad = cantidad
        self.fecha = fecha
        self.total = total

    def guardar_en_base_datos(self):
        # Conectar a la base de datos
        conexion = sql.connect("ventas.db")
        cursor = conexion.cursor()

        # Crear la tabla si no existe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto TEXT,
                precio REAL,
                cantidad INTEGER,
                fecha TEXT,
                total REAL
            )
        ''')

        # Insertar los datos en la tabla
        cursor.execute('''
            INSERT INTO ventas (producto, precio, cantidad, fecha, total)
            VALUES (?, ?, ?, ?, ?)
        ''', (self.producto, self.precio, self.cantidad, self.fecha, self.total))

        # Guardar los cambios y cerrar la conexión
        conexion.commit()
        conexion.close()

    
    def seleccionar_datos(self):
        # Conectar a la base de datos
        conexion = sql.connect("ventas.db")
        cursor = conexion.cursor()

        # Seleccionar todos los datos de la tabla
        cursor.execute('SELECT * FROM ventas')
        datos = cursor.fetchall()

        # Cerrar la conexión
        conexion.close()

        return datos