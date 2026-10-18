from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from ventas.models import (
    Categoria,
    Cliente,
    DetalleVenta,
    Direccion,
    Producto,
    Proveedor,
    TelefonoCliente,
    Venta,
)


class Command(BaseCommand):
    help = "Carga datos ficticios (borra los datos previos de la app ventas)."

    @transaction.atomic
    def handle(self, *args, **options):
        # Limpieza para que el comando sea repetible
        for modelo in (DetalleVenta, Venta, TelefonoCliente, Cliente, Proveedor,
                       Producto, Categoria, Direccion):
            modelo.objects.all().delete()

        # ---------- Categorías ----------
        cats = {}
        for nombre, desc in [
            ("Electrónica", "Dispositivos y accesorios electrónicos."),
            ("Hogar", "Artículos y electrodomésticos para el hogar."),
            ("Oficina", "Útiles y mobiliario de oficina."),
            ("Deportes", "Equipamiento deportivo y accesorios."),
        ]:
            cats[nombre] = Categoria.objects.create(nombre=nombre, descripcion=desc)

        # ---------- Productos ----------
        datos_prod = [
            ("Laptop 15''", "2499.90", 25, "Electrónica"),
            ("Mouse inalámbrico", "49.90", 120, "Electrónica"),
            ("Audífonos Bluetooth", "159.00", 60, "Electrónica"),
            ("Licuadora 600W", "189.50", 40, "Hogar"),
            ("Aspiradora robot", "899.00", 15, "Hogar"),
            ("Silla ergonómica", "529.00", 30, "Oficina"),
            ("Escritorio plegable", "349.90", 18, "Oficina"),
            ("Pelota de fútbol", "69.90", 80, "Deportes"),
            ("Bicicleta de montaña", "1599.00", 0, "Deportes"),  # nunca vendido
        ]
        prods = {}
        for nombre, precio, stock, cat in datos_prod:
            prods[nombre] = Producto.objects.create(
                nombre=nombre, precio_actual=Decimal(precio), stock=stock, categoria=cats[cat]
            )

        # ---------- Proveedores (cada uno provee UN producto; un producto puede tener varios) ----------
        datos_prov = [
            ("P001", "TecnoImport SAC", "Av. Arequipa", "1520", "Lince", "Lima", "014445566", "https://tecnoimport.example.com", "Laptop 15''"),
            ("P002", "Digital Perú", "Jr. Cusco", "340", "Cercado", "Lima", "014447788", "https://digitalperu.example.com", "Laptop 15''"),
            ("P003", "Periféricos del Sur", "Calle Mercaderes", "215", "Cercado", "Arequipa", "054223344", "https://perifericos.example.com", "Mouse inalámbrico"),
            ("P004", "SonidoMax", "Av. Ejército", "801", "Yanahuara", "Arequipa", "054225566", "https://sonidomax.example.com", "Audífonos Bluetooth"),
            ("P005", "Casa Feliz EIRL", "Av. Dolores", "455", "Paucarpata", "Arequipa", "054227788", "", "Licuadora 600W"),
            ("P006", "RoboHogar", "Av. Javier Prado", "2300", "San Isidro", "Lima", "014449900", "https://robohogar.example.com", "Aspiradora robot"),
            ("P007", "Muebles Andinos", "Calle Bolívar", "120", "Cayma", "Arequipa", "054228899", "https://mueblesandinos.example.com", "Silla ergonómica"),
            ("P008", "Oficina Total", "Av. Venezuela", "670", "Breña", "Lima", "014441122", "https://oficinatotal.example.com", "Escritorio plegable"),
            ("P009", "DeporMundo", "Av. Parra", "389", "Cercado", "Arequipa", "054229911", "https://depormundo.example.com", "Pelota de fútbol"),
            ("P010", "BikePro Perú", "Av. La Marina", "1900", "San Miguel", "Lima", "014443322", "https://bikepro.example.com", "Bicicleta de montaña"),
        ]
        for cod, nom, calle, num, comuna, ciudad, tel, web, prod in datos_prov:
            d = Direccion.objects.create(calle=calle, numero=num, comuna=comuna, ciudad=ciudad)
            Proveedor.objects.create(
                codigo=cod, nombre=nom, direccion=d, telefono=tel,
                pagina_web=web, producto=prods[prod],
            )

        # ---------- Clientes (varios teléfonos) ----------
        datos_cli = [
            ("45678901", "María Quispe Huamán", "Calle Ugarte", "210", "Cercado", "Arequipa", ["959111222", "054234567"]),
            ("40123456", "Carlos Mendoza Rojas", "Av. Goyeneche", "845", "Cercado", "Arequipa", ["959333444"]),
            ("72345678", "Lucía Fernández Vega", "Jr. Lampa", "560", "Cercado", "Lima", ["987555666", "014448899", "987777888"]),
            ("43219876", "Jorge Salas Paredes", "Av. Aviación", "1234", "Miraflores", "Lima", ["999000111"]),
            ("70987654", "Ana Torres Cáceres", "Calle Álvarez Thomas", "98", "Yanahuara", "Arequipa", ["959222333", "054221100"]),
            ("46789012", "Diego Ramírez Soto", "Av. Bolognesi", "302", "Tacna", "Tacna", ["952888999"]),
        ]
        clientes = {}
        for cod, nom, calle, num, comuna, ciudad, tels in datos_cli:
            d = Direccion.objects.create(calle=calle, numero=num, comuna=comuna, ciudad=ciudad)
            c = Cliente.objects.create(codigo=cod, nombre=nom, direccion=d)
            for t in tels:
                TelefonoCliente.objects.create(cliente=c, numero=t)
            clientes[cod] = c

        # ---------- Ventas ----------
        # (factura, fecha, cliente, descuento %, [(producto, cantidad, precio_venta|None)])
        datos_ventas = [
            (1001, date(2026, 8, 3), "45678901", "0", [("Laptop 15''", 1, None), ("Mouse inalámbrico", 2, None)]),
            (1002, date(2026, 8, 17), "40123456", "5", [("Licuadora 600W", 1, None), ("Aspiradora robot", 1, "850.00")]),
            (1003, date(2026, 9, 2), "72345678", "10", [("Silla ergonómica", 2, None), ("Escritorio plegable", 1, None)]),
            (1004, date(2026, 9, 21), "45678901", "0", [("Audífonos Bluetooth", 1, "149.00"), ("Pelota de fútbol", 3, None)]),
            (1005, date(2026, 10, 5), "70987654", "2.5", [("Mouse inalámbrico", 4, "45.00"), ("Audífonos Bluetooth", 2, None), ("Licuadora 600W", 1, None)]),
            (1006, date(2026, 10, 12), "43219876", "0", [("Laptop 15''", 2, "2399.90")]),
        ]
        for factura, fecha, cod_cli, desc, items in datos_ventas:
            venta = Venta.objects.create(
                numero_factura=factura, fecha=fecha,
                cliente=clientes[cod_cli], descuento=Decimal(desc),
            )
            for nombre, cant, precio in items:
                producto = prods[nombre]
                DetalleVenta.objects.create(
                    venta=venta, producto=producto, cantidad=cant,
                    precio_venta=Decimal(precio) if precio else producto.precio_actual,
                )

        self.stdout.write(self.style.SUCCESS(
            f"Datos cargados: {Categoria.objects.count()} categorías, "
            f"{Producto.objects.count()} productos, {Proveedor.objects.count()} proveedores, "
            f"{Cliente.objects.count()} clientes, {Venta.objects.count()} ventas."
        ))
