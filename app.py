import flet as ft
from flet import icons
import sqlite3
from datetime import datetime
import csv

class Producto:
    def __init__(self, id, nombre, precio, cantidad):
        self.id = id
        self.nombre = nombre
        self.precio = precio
        self.cantidad = cantidad

class InventarioCajaApp:
    def __init__(self):
        self.conn = sqlite3.connect('inventario_caja.db')
        self.cursor = self.conn.cursor()
        self.crear_tablas()

    
    def crear_tablas(self):
    # Verifica si la columna metodo_pago existe en la tabla ventas
        self.cursor.execute("PRAGMA table_info(ventas)")
        columns = [col[1] for col in self.cursor.fetchall()]
        if 'metodo_pago' not in columns:
            print("Recreando la tabla 'ventas' para agregar la columna 'metodo_pago'")
            self.cursor.execute("DROP TABLE IF EXISTS ventas")
        
        # Crea las tablas
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL,
                precio REAL NOT NULL,
                cantidad INTEGER NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY,
                producto_id INTEGER,
                cantidad INTEGER,
                total REAL,
                metodo_pago TEXT,
                fecha TEXT,
                FOREIGN KEY (producto_id) REFERENCES productos (id)
            )
        ''')
        self.conn.commit()

    
    
    def agregar_producto(self, nombre, precio, cantidad):
        try:
            self.cursor.execute(
                'INSERT INTO productos (nombre, precio, cantidad) VALUES (?, ?, ?)',
                (nombre, precio, cantidad)
            )
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def actualizar_producto(self, id, nombre, precio, cantidad):
        try:
            self.cursor.execute(
                'UPDATE productos SET nombre = ?, precio = ?, cantidad = ? WHERE id = ?',
                (nombre, precio, cantidad, id)
            )
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def eliminar_producto(self, id):
        try:
            self.cursor.execute('DELETE FROM productos WHERE id = ?', (id,))
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def obtener_productos(self):
        try:
            self.cursor.execute('SELECT * FROM productos')
            return [Producto(*row) for row in self.cursor.fetchall()]
        except sqlite3.Error:
            return []

    def registrar_venta(self, producto_id, cantidad, total, metodo_pago):
        try:
            fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.execute('''
                INSERT INTO ventas (producto_id, cantidad, total, metodo_pago, fecha)
                VALUES (?, ?, ?, ?, ?)
            ''', (producto_id, cantidad, total, metodo_pago, fecha))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error al registrar la venta: {e}")
            return False

    def obtener_totales_por_metodo_pago(self):
        try:
            self.cursor.execute(
                'SELECT metodo_pago, SUM(total) FROM ventas GROUP BY metodo_pago'
            )
            return {metodo_pago: total for metodo_pago, total in self.cursor.fetchall()}
        except sqlite3.Error:
            return {}

    def obtener_cuadre_caja(self):
        try:
            self.cursor.execute(
                "SELECT SUM(total) FROM ventas WHERE DATE(fecha) = DATE('now')"
            )
            return self.cursor.fetchone()[0] or 0
        except sqlite3.Error:
            return 0


    def registrar_venta(self, producto_id, cantidad, total, metodo_pago):
        try:
            fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.execute('''
                INSERT INTO ventas (producto_id, cantidad, total, metodo_pago, fecha)
                VALUES (?, ?, ?, ?, ?)
            ''', (producto_id, cantidad, total, metodo_pago, fecha))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error al registrar la venta: {e}")
            return False

    def obtener_totales_por_metodo_pago(self):
        try:
            self.cursor.execute(
                'SELECT metodo_pago, SUM(total) FROM ventas GROUP BY metodo_pago'
            )
            return {metodo_pago: total for metodo_pago, total in self.cursor.fetchall()}
        except sqlite3.Error:
            return {}

    def obtener_cuadre_caja(self):
        try:
            self.cursor.execute(
                "SELECT SUM(total) FROM ventas WHERE DATE(fecha) = DATE('now')"
            )
            return self.cursor.fetchone()[0] or 0
        except sqlite3.Error:
            return 0

    def generar_reporte_csv(self, filename='reporte_inventario.csv'):
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['ID', 'Nombre', 'Precio', 'Cantidad', 'Valor Total'])
                for producto in self.obtener_productos():
                    writer.writerow([
                        producto.id,
                        producto.nombre,
                        producto.precio,
                        producto.cantidad,
                        producto.precio * producto.cantidad
                    ])
            return True
        except IOError:
            return False


def main(page: ft.Page):
    app = InventarioCajaApp()

    page.title = "Inventario y Cuadre de Caja"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 900
    page.window_height = 800

    snack_bar = ft.SnackBar(
        content=ft.Text(""),
        action="Cerrar",
        action_color=ft.colors.WHITE
    )
    page.overlay.append(snack_bar)

    def mostrar_toast(mensaje, color=ft.colors.GREEN):
        snack_bar.content = ft.Text(mensaje)
        snack_bar.bgcolor = color
        snack_bar.open = True
        page.update()

    def cambiar_tema(e):
        page.theme_mode = (
            ft.ThemeMode.DARK
            if page.theme_mode == ft.ThemeMode.LIGHT
            else ft.ThemeMode.LIGHT
        )
        page.update()

    tema_button = ft.IconButton(
        icon=icons.BRIGHTNESS_6,
        on_click=cambiar_tema,
        tooltip="Cambiar tema",
    )

    nombre_input = ft.TextField(
        label="Nombre del producto",
        expand=1,
        prefix_icon=icons.INVENTORY
    )

    precio_input = ft.TextField(
        label="Precio",
        expand=1,
        prefix_icon=icons.ATTACH_MONEY
    )

    cantidad_input = ft.TextField(
        label="Cantidad",
        expand=1,
        prefix_icon=icons.NUMBERS
    )

    buscar_input = ft.TextField(
        label="Buscar producto",
        expand=1,
        prefix_icon=icons.SEARCH
    )

    metodo_pago_dropdown = ft.Dropdown(
        label="Método de Pago",
        options=[
            ft.dropdown.Option("efectivo"),
            ft.dropdown.Option("debito"),
            ft.dropdown.Option("credito"),
        ],
        expand=True,
    )

    productos_row = ft.Row(
        wrap=True,
        scroll="auto",
        expand=True,
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )

    cuadre_texto = ft.Text(size=20)
    total_inventario_texto = ft.Text(size=20)
    totales_pago_texto = ft.Text(size=20)

    def actualizar_lista_productos():
        productos_row.controls.clear()
        for producto in app.obtener_productos():
            productos_row.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.ListTile(
                                leading=ft.Icon(icons.SHOPPING_BASKET),
                                title=ft.Text(
                                    f"{producto.nombre}",
                                    size=16,
                                    weight="bold"
                                ),
                                subtitle=ft.Text(
                                    f"Precio: ${producto.precio:.2f}\n"
                                    f"Cantidad: {producto.cantidad}"
                                ),
                            ),
                            ft.Row([
                                ft.IconButton(
                                    icons.EDIT,
                                    on_click=lambda _, p=producto: editar_producto(p)
                                ),
                                ft.IconButton(
                                    icons.DELETE,
                                    on_click=lambda _, id=producto.id: eliminar_producto(id)
                                ),
                                ft.IconButton(
                                    icons.SHOPPING_CART,
                                    on_click=lambda _, p=producto: registrar_venta_dialog(p)
                                )
                            ], alignment=ft.MainAxisAlignment.END)
                        ]),
                        width=250,
                        padding=10,
                    )
                )
            )
        page.update()

    def actualizar_totales():
        totales = app.obtener_totales_por_metodo_pago()
        totales_texto = "Totales por método de pago:\n"
        for metodo, total in totales.items():
            totales_texto += f"{metodo.capitalize()}: ${total:.2f}\n"
        totales_pago_texto.value = totales_texto
        page.update()

    def agregar_producto(e):
        try:
            nombre = nombre_input.value
            precio = float(precio_input.value)
            cantidad = int(cantidad_input.value)
            if nombre and precio > 0 and cantidad >= 0:
                if app.agregar_producto(nombre, precio, cantidad):
                    actualizar_lista_productos()
                    nombre_input.value = ""
                    precio_input.value = ""
                    cantidad_input.value = ""
                    actualizar_cuadre()
                    calcular_total_inventario()
                    mostrar_toast("Producto agregado exitosamente")
                else:
                    mostrar_toast("Error al agregar el producto", ft.colors.RED_400)
            else:
                mostrar_toast(
                    "Por favor, ingrese valores válidos",
                    ft.colors.ORANGE_400
                )
        except ValueError:
            mostrar_toast(
                "Por favor, ingrese valores numéricos válidos para precio y cantidad",
                ft.colors.RED_400
            )
        page.update()

    def editar_producto(producto):
        nombre_editar = ft.TextField(
            value=producto.nombre,
            label="Nombre del producto"
        )
        precio_editar = ft.TextField(
            value=str(producto.precio),
            label="Precio"
        )
        cantidad_editar = ft.TextField(
            value=str(producto.cantidad),
            label="Cantidad"
        )

        def guardar_cambios(e):
            try:
                nombre = nombre_editar.value
                precio = float(precio_editar.value)
                cantidad = int(cantidad_editar.value)
                if nombre and precio > 0 and cantidad >= 0:
                    if app.actualizar_producto(
                        producto.id,
                        nombre,
                        precio,
                        cantidad
                    ):
                        actualizar_lista_productos()
                        actualizar_cuadre()
                        calcular_total_inventario()
                        mostrar_toast("Producto actualizado exitosamente")
                        dialog.open = False
                    else:
                        mostrar_toast(
                            "Error al actualizar el producto",
                            ft.colors.RED_400
                        )
                else:
                    mostrar_toast(
                        "Por favor, ingrese valores válidos",
                        ft.colors.ORANGE_400
                    )
            except ValueError:
                mostrar_toast(
                    "Por favor, ingrese valores numéricos válidos",
                    ft.colors.RED_400
                )
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Editar Producto"),
            content=ft.Column([nombre_editar, precio_editar, cantidad_editar]),
            actions=[
                ft.TextButton("Guardar", on_click=guardar_cambios),
                ft.TextButton("Cancelar", on_click=lambda e: dialog.close()),
            ],
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def eliminar_producto(id):
        def confirmar_eliminacion(e):
            if app.eliminar_producto(id):
                actualizar_lista_productos()
                actualizar_cuadre()
                calcular_total_inventario()
                mostrar_toast("Producto eliminado exitosamente")
                dialog.open = False
            else:
                mostrar_toast("Error al eliminar el producto", ft.colors.RED_400)
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text("¿Está seguro de que desea eliminar este producto?"),
            actions=[
                ft.TextButton("Sí", on_click=confirmar_eliminacion),
                ft.TextButton("No", on_click=lambda e: dialog.close()),
            ],
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def registrar_venta_dialog(producto):
        cantidad_venta_input = ft.TextField(
            label="Cantidad a vender",
            expand=1,
            prefix_icon=icons.NUMBERS
        )

        def registrar_venta(e):
            try:
                if not metodo_pago_dropdown.value:
                    mostrar_toast(
                        "Por favor seleccione un método de pago",
                        ft.colors.ORANGE_400
                    )
                    return

                cantidad = int(cantidad_venta_input.value)
                if cantidad > 0 and cantidad <= producto.cantidad:
                    total = producto.precio * cantidad
                    metodo_pago = metodo_pago_dropdown.value
                    if app.registrar_venta(
                        producto.id,
                        cantidad,
                        total,
                        metodo_pago
                    ):
                        nueva_cantidad = producto.cantidad - cantidad
                        app.actualizar_producto(
                            producto.id,
                            producto.nombre,
                            producto.precio,
                            nueva_cantidad
                        )
                        actualizar_lista_productos()
                        actualizar_cuadre()
                        actualizar_totales()
                        calcular_total_inventario()
                        mostrar_toast("Venta registrada exitosamente")
                        dialog.open = False
                    else:
                        mostrar_toast(
                            "Error al registrar la venta",
                            ft.colors.RED_400
                        )
                else:
                    mostrar_toast(
                        "Cantidad no válida o insuficiente stock",
                        ft.colors.ORANGE_400
                    )
            except ValueError:
                mostrar_toast(
                    "Por favor, ingrese un número válido",
                    ft.colors.RED_400
                )
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text(f"Registrar Venta - {producto.nombre}"),
            content=ft.Column([cantidad_venta_input, metodo_pago_dropdown]),
            actions=[
                ft.TextButton("Registrar", on_click=registrar_venta),
                ft.TextButton("Cancelar", on_click=lambda e: dialog.close()),
            ],
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def actualizar_cuadre():
        cuadre = app.obtener_cuadre_caja()
        cuadre_texto.value = f"Cuadre de Caja: ${cuadre:.2f}"
        actualizar_totales()
        page.update()

    def calcular_total_inventario():
        total_inventario = sum(
            producto.precio * producto.cantidad
            for producto in app.obtener_productos()
        )
        total_inventario_texto.value = f"Total Inventario: ${total_inventario:.2f}"
        page.update()
    def buscar_producto(e):
        query = buscar_input.value.lower()
        productos_row.controls.clear()
        for producto in app.obtener_productos():
            if query in producto.nombre.lower():
                productos_row.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.ListTile(
                                    leading=ft.Icon(icons.SHOPPING_BASKET),
                                    title=ft.Text(
                                        f"{producto.nombre}",
                                        size=16,
                                        weight="bold"
                                    ),
                                    subtitle=ft.Text(
                                        f"Precio: ${producto.precio:.2f}\n"
                                        f"Cantidad: {producto.cantidad}"
                                    ),
                                ),
                                ft.Row([
                                    ft.IconButton(
                                        icons.EDIT,
                                        on_click=lambda _, p=producto: editar_producto(p)
                                    ),
                                    ft.IconButton(
                                        icons.DELETE,
                                        on_click=lambda _, id=producto.id: eliminar_producto(id)
                                    ),
                                    ft.IconButton(
                                        icons.SHOPPING_CART,
                                        on_click=lambda _, p=producto: registrar_venta_dialog(p)
                                    )
                                ], alignment=ft.MainAxisAlignment.END)
                            ]),
                            width=250,
                            padding=10,
                        )
                    )
                )
        page.update()

    def exportar_reporte(e):
        if app.generar_reporte_csv():
            mostrar_toast("Reporte generado exitosamente")
        else:
            mostrar_toast("Error al generar el reporte", ft.colors.RED_400)

    # Creación de la interfaz principal
    page.add(
        ft.AppBar(
            title=ft.Text("Inventario y Cuadre de Caja"),
            actions=[
                ft.IconButton(
                    icon=icons.FILE_DOWNLOAD,
                    on_click=exportar_reporte,
                    tooltip="Exportar Reporte"
                ),
                tema_button
            ],
        ),
        ft.Container(
            content=ft.Column([
                ft.Row([
                    buscar_input,
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(),
                ft.Text(
                    "Agregar Nuevo Producto",
                    size=20,
                    weight="bold"
                ),
                ft.Row([
                    nombre_input,
                    precio_input,
                    cantidad_input,
                    ft.IconButton(
                        icon=icons.ADD_CIRCLE,
                        on_click=agregar_producto,
                        tooltip="Agregar Producto",
                        icon_size=40,
                    )
                ]),
                ft.Divider(),
                ft.Text(
                    "Productos en Inventario",
                    size=20,
                    weight="bold"
                ),
                productos_row,
                ft.Divider(),
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "Resumen Financiero",
                            size=20,
                            weight="bold"
                        ),
                        cuadre_texto,
                        total_inventario_texto,
                        totales_pago_texto,
                    ]),
                    padding=20,
                    border=ft.border.all(1, ft.colors.OUTLINE),
                    border_radius=10,
                )
            ]),
            padding=20,
        )
    )

    # Configurar el evento de búsqueda
    buscar_input.on_change = buscar_producto

    # Inicializar la interfaz
    actualizar_lista_productos()
    actualizar_cuadre()
    calcular_total_inventario()
    actualizar_totales()


if __name__ == "__main__":
    ft.app(target=main)