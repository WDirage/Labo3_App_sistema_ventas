# Sistema de Ventas (Django)

## Instalación y ejecución

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py makemigrations ventas
python manage.py migrate
python manage.py cargar_datos          # datos ficticios
python manage.py createsuperuser       # para entrar al admin
python manage.py runserver
```

Panel de administración: http://127.0.0.1:8000/admin/

## Esquema de clases

| Clase | Atributos principales | Relaciones |
|---|---|---|
| Direccion | calle, numero, comuna, ciudad | usada por Cliente y Proveedor |
| Categoria | id, nombre, descripcion | 1 categoría → N productos |
| Producto | id, nombre, precio_actual, stock | N productos → 1 categoría |
| Proveedor | codigo (único), nombre, telefono, pagina_web | N proveedores → 1 producto; 1 dirección |
| Cliente | codigo (único), nombre | 1 dirección; N teléfonos |
| TelefonoCliente | numero | N teléfonos → 1 cliente |
| Venta | numero_factura (único), fecha, descuento (%), monto_final | N ventas → 1 cliente |
| DetalleVenta | precio_venta, cantidad, monto_total | tabla intermedia Venta ↔ Producto (N:M) |

`monto_total = precio_venta × cantidad` y
`monto_final = suma(monto_total) × (100 − descuento) / 100`; ambos se calculan automáticamente.
