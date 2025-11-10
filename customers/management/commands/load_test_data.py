import random
from decimal import Decimal
from faker import Faker

from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

# Importa todos tus modelos
from customers.models import (
    TipoDocumento, TipoTelefono, Cliente, Documento, Telefono,
    CategoriaProducto, Producto, Compra, DetalleCompra
)

# Configura Faker para español (Colombia)
fake = Faker('es_CO')

class Command(BaseCommand):
    help = 'Generates test data for the customers application.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Delete all existing data before generating new data (except catalogs).',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("This command cannot be run in production.")

        is_clean = options['clean']

        if is_clean:
            self.stdout.write(self.style.WARNING('Cleaning database...'))
            # Borra en orden inverso de dependencia
            DetalleCompra.objects.all().delete()
            Compra.objects.all().delete()
            Telefono.objects.all().delete()
            Documento.objects.all().delete()
            Cliente.objects.all().delete()
            Producto.objects.all().delete()
            CategoriaProducto.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Database cleaned.'))

        # --- 1. Cargar Catálogos Base (Tus JSON) ---
        # Asumimos que TIPO_DOCUMENTO y TIPO_TELEFONO ya fueron cargados
        # desde tu 'catalogos.json' (usando manage.py loaddata)

        tipos_doc = list(TipoDocumento.objects.filter(activo=True))
        tipos_tel = list(TipoTelefono.objects.all())

        if not tipos_doc or not tipos_tel:
            self.stdout.write(self.style.ERROR(
                'Base catalogs (TipoDocumento, TipoTelefono) not found.'
            ))
            self.stdout.write(self.style.WARNING(
                'Please load them first using: python manage.py loaddata catalogos.json'
            ))
            return

        # --- 2. Crear CategoriaProducto ---
        self.stdout.write('Creating CategoriaProducto...')
        categorias_data = [
            ('Electrónica', 'Dispositivos y accesorios electrónicos.'),
            ('Ropa y Accesorios', 'Vestimenta para todas las edades.'),
            ('Hogar y Jardín', 'Artículos para el hogar.'),
            ('Servicios Profesionales', 'Consultoría, desarrollo, etc.'),
        ]
        categorias = []
        for nombre, desc in categorias_data:
            cat, _ = CategoriaProducto.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': desc}
            )
            categorias.append(cat)

        # --- 3. Crear Producto ---
        self.stdout.write('Creating Producto...')
        productos = []
        for i in range(25):
            cat = random.choice(categorias)
            es_servicio = cat.nombre == 'Servicios Profesionales'
            prod = Producto.objects.create(
                codigo=f'PROD-{fake.ean(length=8)}',
                nombre=fake.bs().capitalize(),
                categoria=cat,
                precio_base=Decimal(random.randrange(10000, 500000)),
                es_servicio=es_servicio,
                activo=True
            )
            productos.append(prod)

        # --- 4. Crear Cliente, Documento y Telefono ---
        self.stdout.write('Creating Cliente, Documento, and Telefono...')
        clientes = []
        for _ in range(30): # Crear 30 clientes
            cliente = Cliente.objects.create(
                nombre=fake.first_name(),
                apellido=fake.last_name(),
                correo=fake.unique.email(),
            )
            clientes.append(cliente)

            # Crear Documento principal
            Documento.objects.create(
                cliente=cliente,
                tipo_documento=random.choice(tipos_doc),
                numero_documento=fake.ssn().replace('-', ''),
                principal=True
            )

            # Crear Telefono principal
            Telefono.objects.create(
                cliente=cliente,
                phone_type=random.choice(tipos_tel),
                numero=fake.phone_number(),
                principal=True
            )

        # --- 5. Crear Compra y DetalleCompra ---
        self.stdout.write('Creating Compra and DetalleCompra...')
        for _ in range(50): # Crear 50 compras
            cliente = random.choice(clientes)

            # Crear cabecera de Compra (con totales en 0 temporalmente)
            compra = Compra.objects.create(
                cliente=cliente,
                numero_factura=f'FAC-{fake.ean(length=13)}',
                estado=random.choice(['PEN', 'PAG', 'CAN']),
            )

            # Crear detalles de la compra (1 a 5 items)
            num_items = random.randint(1, 5)
            compra_subtotal = Decimal('0.00')

            detalles_a_crear = []
            for _ in range(num_items):
                producto = random.choice(productos)
                cantidad = Decimal(random.randint(1, 3))

                # Usar el precio base del producto como precio unitario
                precio_unitario = producto.precio_base 
                item_subtotal = cantidad * precio_unitario
                compra_subtotal += item_subtotal

                detalles_a_crear.append(
                    DetalleCompra(
                        compra=compra,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=precio_unitario
                    )
                )

            # Crear detalles en lote
            DetalleCompra.objects.bulk_create(detalles_a_crear)

            # Calcular totales y actualizar la Compra
            # Asumamos un IVA fijo del 19% para el ejemplo
            compra_impuestos = compra_subtotal * Decimal('0.19')
            compra_total = compra_subtotal + compra_impuestos

            compra.subtotal = compra_subtotal
            compra.impuestos = compra_impuestos
            compra.total = compra_total
            compra.save()

        self.stdout.write(self.style.SUCCESS(
            f'Successfully generated test data. {len(clientes)} clients, {len(productos)} products, 50 orders.'
        ))