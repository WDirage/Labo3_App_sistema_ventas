from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Direccion(models.Model):
    """Dirección reutilizable por clientes y proveedores."""

    calle = models.CharField(max_length=120)
    numero = models.CharField(max_length=10)
    comuna = models.CharField(max_length=80)
    ciudad = models.CharField(max_length=80)

    class Meta:
        verbose_name = "dirección"
        verbose_name_plural = "direcciones"

    def __str__(self):
        return f"{self.calle} {self.numero}, {self.comuna}, {self.ciudad}"


class Categoria(models.Model):
    nombre = models.CharField(max_length=80, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = "categoría"
        verbose_name_plural = "categorías"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=120)
    precio_actual = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))]
    )
    stock = models.PositiveIntegerField(default=0)
    # Un producto pertenece a UNA categoría; una categoría clasifica VARIOS productos.
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, related_name="productos"
    )

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    codigo = models.CharField("código", max_length=20, unique=True)  # equivalente al DNI
    nombre = models.CharField(max_length=120)
    direccion = models.ForeignKey(
        Direccion, on_delete=models.PROTECT, related_name="proveedores"
    )
    telefono = models.CharField("teléfono", max_length=20)
    pagina_web = models.URLField("página web", blank=True)
    # Un proveedor provee UN solo producto; un producto lo comercializan VARIOS proveedores.
    producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT, related_name="proveedores"
    )

    class Meta:
        verbose_name_plural = "proveedores"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"


class Cliente(models.Model):
    codigo = models.CharField("código", max_length=20, unique=True)  # equivalente al DNI
    nombre = models.CharField(max_length=120)
    direccion = models.ForeignKey(
        Direccion, on_delete=models.PROTECT, related_name="clientes"
    )

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"


class TelefonoCliente(models.Model):
    """Un cliente puede tener varios teléfonos de contacto."""

    cliente = models.ForeignKey(
        Cliente, on_delete=models.CASCADE, related_name="telefonos"
    )
    numero = models.CharField("número", max_length=20)

    class Meta:
        verbose_name = "teléfono de cliente"
        verbose_name_plural = "teléfonos de clientes"
        unique_together = ("cliente", "numero")

    def __str__(self):
        return f"{self.numero} - {self.cliente.nombre}"


class Venta(models.Model):
    numero_factura = models.PositiveIntegerField("número de factura", unique=True)
    fecha = models.DateField()
    # Una venta tiene UN cliente; un cliente puede tener VARIAS ventas.
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="ventas")
    descuento = models.DecimalField(
        "descuento (%)",
        max_digits=5,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
    )
    monto_final = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0"), editable=False
    )
    # Una venta se compone de VARIOS productos y un producto puede estar en VARIAS ventas
    # (relación muchos a muchos con atributos, a través de DetalleVenta).
    productos = models.ManyToManyField(
        Producto, through="DetalleVenta", related_name="ventas"
    )

    class Meta:
        ordering = ["-fecha", "-numero_factura"]

    def __str__(self):
        return f"Factura N° {self.numero_factura}"

    def recalcular_monto(self):
        """monto_final = suma de montos de detalle menos el descuento porcentual."""
        subtotal = sum((d.monto_total for d in self.detalles.all()), Decimal("0"))
        self.monto_final = (subtotal * (Decimal("100") - self.descuento) / Decimal("100")).quantize(
            Decimal("0.01")
        )
        self.save(update_fields=["monto_final"])


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT, related_name="detalles"
    )
    # Precio del producto al momento de la venta (puede diferir del precio actual).
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    monto_total = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    class Meta:
        verbose_name = "detalle de venta"
        verbose_name_plural = "detalles de venta"
        unique_together = ("venta", "producto")

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} ({self.venta})"

    def save(self, *args, **kwargs):
        if not self.precio_venta:
            self.precio_venta = self.producto.precio_actual
        self.monto_total = self.precio_venta * self.cantidad
        super().save(*args, **kwargs)
        self.venta.recalcular_monto()

    def delete(self, *args, **kwargs):
        venta = self.venta
        super().delete(*args, **kwargs)
        venta.recalcular_monto()
