from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineAvatarIconListItem, IconRightWidget
from kivymd.uix.boxlayout import MDBoxLayout as Box
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.button import MDRaisedButton
import json
import sqlite3 as sql
from datetime import datetime
import os
from kivy.uix.widget import Widget
from kivymd.uix.label import MDLabel
from kivy.metrics import dp


class ProductoItem(OneLineAvatarIconListItem):
    nombre = StringProperty("")
    precio = NumericProperty(0)
    cantidad = NumericProperty(0)
    index = NumericProperty(0)

class EditarProducto(Box):
    nombre = StringProperty("")
    precio = NumericProperty(0)
    cantidad = NumericProperty(0)

class MainApp(MDBoxLayout):
    productos = ListProperty()
    total = NumericProperty(0)
    dialog = None
    producto_actual = None
    index = NumericProperty(0)

    def guardar_ganancia(self, index):
        fecha = datetime.now().strftime("%d-%m-%Y")
        ganancia = {
            "fecha": fecha,
            "producto": self.productos[index]["nombre"],
            "cantidad": self.productos[index]["cantidad"],
            "total": self.total
        }

        #AHORAA PRECISO QUE AL GUARDAR NO GUARDE SOLO EL INDICE 0,
        #SINO TODO LO QUE ESTÉ
        print(index)

        archivo = "ganancias.json"

        # Si ya existe el archivo, lo abrimos, sino creamos uno
        if os.path.exists(archivo):
            with open(archivo, "r") as f:
                datos = json.load(f)
        else:
            datos = []

        datos.append(ganancia)

        with open(archivo, "w") as f:
            json.dump(datos, f, indent=4)

        print(f"Ganancia guardada: {ganancia}")

    def mostrar_dia_de_la_semana(self) : 

        hoy = datetime.now()

        dias_semana = {
            0: "Lunes",
            1: "Martes",
            2: "Miércoles",
            3: "Jueves",
            4: "Viernes",
            5: "Sábado",
            6: "Domingo"
        }

        dia_nombre = dias_semana[hoy.weekday()]

        return dia_nombre


    def mostrar_historial (self) : 
        
        #Hacer una función que corrobore si el archivo .json está o no.
        #Luego se utiliza el archivo para mostrar el historial de ganancias directamente.
        # Leer JSON

        dia_de_la_semana = self.mostrar_dia_de_la_semana()

        try:
            with open('ganancias.json', 'r', encoding='utf-8') as f:
                datos = json.load(f)
        except Exception as e:
            datos = [{"fecha": "", "evento": f"Error: {e}", "total": ""}]

        # Crear MDList con datos
        lista = MDList()
        for item in datos:
            texto = f"{item['producto']} | {item['cantidad']} | ${item['total']} | {dia_de_la_semana} {item['fecha']}"
            lista.add_widget(OneLineListItem(text=texto))

        # ScrollView que contiene la lista
        scroll = MDScrollView()
        scroll.size_hint = (1, None)
        scroll.height = 300  # Altura fija para que no se solape con el título
        scroll.add_widget(lista)

        # Crear/actualizar el diálogo
        if self.dialog:
            self.dialog.dismiss()

        self.dialog = MDDialog(
            title="Historial de Ventas",
            type="custom",
            content_cls=scroll,
            buttons=[
                MDRaisedButton(text="Cerrar", on_release=lambda x: self.dialog.dismiss())
            ],
        )
        self.dialog.open()


    def agregar_producto(self):
        self.productos.append({"nombre": "Nuevo producto", "precio": 0, "cantidad": 0})
        self.actualizar_total()

    def eliminar_producto(self, index):
        del self.productos[index]
        self.actualizar_total()

    def aumentar_cantidad(self, index):
        self.productos[index]["cantidad"] += 1
        self.actualizar_total()

    def disminuir_cantidad(self, index):
        if self.productos[index]["cantidad"] > 0:
            self.productos[index]["cantidad"] -= 1
            self.actualizar_total()

    def editar_producto(self, index):
        self.producto_actual = index
        producto = self.productos[index]

        self.dialog = MDDialog(
            title="Editar Producto",
            type="custom",
            content_cls=EditarProducto(
                nombre="",
                precio=producto['precio'],
                cantidad=producto['cantidad']
            ),
            buttons=[
                MDFlatButton(text="CANCELAR", on_release=self.cerrar_dialogo),
                MDFlatButton(text="GUARDAR", on_release=self.guardar_cambios)
            ],
        )
        self.dialog.open()

    def guardar_cambios(self, *args):
        datos = self.dialog.content_cls
        self.productos[self.producto_actual]["nombre"] = datos.ids.nombre.text
        self.productos[self.producto_actual]["precio"] = float(datos.ids.precio.text)
        self.productos[self.producto_actual]["cantidad"] = int(datos.ids.cantidad.text)
        self.actualizar_total()
        self.dialog.dismiss()

    def cerrar_dialogo(self, *args):
        self.dialog.dismiss()

    def actualizar_total(self):
        self.total = sum(p["precio"] * p["cantidad"] for p in self.productos)

        productos_layout = self.ids.productos_layout
        productos_layout.clear_widgets()
        espacio_vacio ="                                                         "

        for i, producto in enumerate(self.productos):
            item = ProductoItem(
                text= espacio_vacio + f"{producto['nombre']} - ${producto['precio']:.2f} x {producto['cantidad']}",
                nombre=producto["nombre"],
                precio=producto["precio"],
                cantidad=producto["cantidad"],
                index=i
            )
            icon = IconRightWidget(icon="cart")
            item.add_widget(icon)
            productos_layout.add_widget(item)

class NegocioApp(MDApp):
    icon = 'chango.png'
    def build(self):
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.theme_style = "Light"  # También puedes usar "Dark"
        return MainApp()

if __name__ == "__main__":
    NegocioApp().run()