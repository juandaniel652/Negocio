from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineAvatarIconListItem, IconRightWidget
from kivymd.uix.boxlayout import MDBoxLayout as Box
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.button import MDRaisedButton
import json
import database
from datetime import datetime
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget

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

    def crear_caja_emergente (self, titulo, texto) : 

        content = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        message = Label(
        text = texto,
        font_size = '18sp',
        color = (1, 1, 1, 1),
        halign = 'center',
        valign = 'middle'
        )

        message.bind(size=message.setter('text_size'))

        btn_close = Button(
            text = "Cerrar",
            size_hint_y = None,
            height = 45,
            background_color = (0.2, 0.6, 0.86, 1),  # azul moderno
            color = (1, 1, 1, 1),  # texto blanco
            bold = True
        )

        content.add_widget(message)
        content.add_widget(btn_close)

        popup = Popup(
            title=titulo,
            title_align='center',
            title_color=(1, 1, 1, 1),
            background='atlas://data/images/defaulttheme/button_pressed',  # transparente
            separator_color=(0.2, 0.6, 0.86, 1),
            content=content,
            size_hint=(None, None),
            size=(350, 220),
            auto_dismiss=False
        )

        btn_close.bind(on_release=popup.dismiss)
        popup.open()


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

    
    def mostrar_fecha_actual (self) : 

        fecha = datetime.now().strftime("%d-%m-%Y")
        return fecha
    

    def guardar_ganancia(self, index):
        
        nombre_del_dia = self.mostrar_dia_de_la_semana()
        fecha = self.mostrar_fecha_actual()
        fecha_con_dia = f"{nombre_del_dia} {fecha}"

        try: 

            datos = database.datos_guardados(self.productos[index]["nombre"], 
                                            self.productos[index]["precio"],
                                            self.productos[index]["cantidad"],
                                            fecha_con_dia,
                                            self.total)    

            datos.guardar_en_base_datos()

            self.crear_caja_emergente("Mensaje", "Ganancia guardada en la base de datos.")
        
        except : 

            self.crear_caja_emergente("Error", "No se pudo guardar la ganancia en la base de datos.")
        

    def mostrar_historial (self) : 

        try:
            
            base_de_datos = database.datos_guardados("", 0, 0, "", 0)
            datos = base_de_datos.seleccionar_datos()

            # Crear MDList con datos
            lista = MDList()
            for item in datos:
                texto = f"{item[1]} | {item[2]} | {item[3]} | ${item[5]} | {item[4]}"
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
        
        except  :

            self.crear_caja_emergente("Error", "No hay historial de ventas.")


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