import database

llamada = database.datos_guardados("", 0, 0, "", 0)
datos = llamada.seleccionar_datos()
print(datos[0][1])