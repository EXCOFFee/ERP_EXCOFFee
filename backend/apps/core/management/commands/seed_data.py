# ========================================================
# SISTEMA ERP UNIVERSAL - Comando para generar datos de prueba
# ========================================================

from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'Genera datos de prueba para el sistema ERP'

    def handle(self, *args, **options):
        self.stdout.write('Generando datos de prueba...')
        
        with transaction.atomic():
            self.create_inventory_data()
            self.create_hr_data()
            self.create_finance_data()
            self.create_sales_data()
            self.create_purchasing_data()
        
        self.stdout.write(self.style.SUCCESS('Datos de prueba generados correctamente'))

    def create_inventory_data(self):
        """Crear datos de inventario"""
        from apps.inventory.models import (
            Category, UnitOfMeasure, Warehouse, Product
        )
        
        self.stdout.write('  - Creando categorías...')
        categories = [
            {'code': 'ELEC', 'name': 'Electrónica', 'description': 'Productos electrónicos'},
            {'code': 'ROPA', 'name': 'Ropa y Accesorios', 'description': 'Vestimenta'},
            {'code': 'ALIM', 'name': 'Alimentos', 'description': 'Productos alimenticios'},
            {'code': 'HOGAR', 'name': 'Hogar', 'description': 'Artículos para el hogar'},
            {'code': 'OFIC', 'name': 'Oficina', 'description': 'Suministros de oficina'},
        ]
        cat_objs = []
        for cat in categories:
            obj, _ = Category.objects.get_or_create(code=cat['code'], defaults=cat)
            cat_objs.append(obj)
        
        self.stdout.write('  - Creando unidades de medida...')
        units = [
            {'name': 'Unidad', 'abbreviation': 'und', 'is_base_unit': True},
            {'name': 'Kilogramo', 'abbreviation': 'kg', 'is_base_unit': False},
            {'name': 'Litro', 'abbreviation': 'lt', 'is_base_unit': False},
            {'name': 'Metro', 'abbreviation': 'm', 'is_base_unit': False},
            {'name': 'Caja', 'abbreviation': 'cj', 'is_base_unit': False},
        ]
        unit_objs = []
        for unit in units:
            obj, _ = UnitOfMeasure.objects.get_or_create(name=unit['name'], defaults=unit)
            unit_objs.append(obj)
        
        self.stdout.write('  - Creando almacenes...')
        warehouses = [
            {'code': 'ALM01', 'name': 'Almacén Principal', 'address': 'Av. Principal 123', 'city': 'Ciudad', 'state': 'Estado', 'postal_code': '12345', 'country': 'México'},
            {'code': 'ALM02', 'name': 'Almacén Secundario', 'address': 'Calle Comercial 456', 'city': 'Ciudad', 'state': 'Estado', 'postal_code': '12346', 'country': 'México'},
            {'code': 'TIENDA', 'name': 'Tienda Central', 'address': 'Centro Comercial 789', 'city': 'Ciudad', 'state': 'Estado', 'postal_code': '12347', 'country': 'México'},
        ]
        wh_objs = []
        for wh in warehouses:
            obj, _ = Warehouse.objects.get_or_create(code=wh['code'], defaults=wh)
            wh_objs.append(obj)
        
        self.stdout.write('  - Creando productos...')
        products = [
            {'sku': 'PROD001', 'name': 'Laptop HP 15"', 'category': cat_objs[0], 'brand': 'HP', 'unit_of_measure': unit_objs[0], 'sale_price': Decimal('1200.00'), 'cost_price': Decimal('900.00')},
            {'sku': 'PROD002', 'name': 'Monitor Samsung 24"', 'category': cat_objs[0], 'brand': 'Samsung', 'unit_of_measure': unit_objs[0], 'sale_price': Decimal('350.00'), 'cost_price': Decimal('250.00')},
            {'sku': 'PROD003', 'name': 'Teclado inalámbrico', 'category': cat_objs[0], 'brand': 'LG', 'unit_of_measure': unit_objs[0], 'sale_price': Decimal('45.00'), 'cost_price': Decimal('30.00')},
            {'sku': 'PROD004', 'name': 'Mouse óptico', 'category': cat_objs[0], 'brand': 'LG', 'unit_of_measure': unit_objs[0], 'sale_price': Decimal('25.00'), 'cost_price': Decimal('15.00')},
            {'sku': 'PROD005', 'name': 'Auriculares Sony', 'category': cat_objs[0], 'brand': 'Sony', 'unit_of_measure': unit_objs[0], 'sale_price': Decimal('150.00'), 'cost_price': Decimal('100.00')},
            {'sku': 'PROD006', 'name': 'Cámara web HD', 'category': cat_objs[0], 'brand': 'LG', 'unit_of_measure': unit_objs[0], 'sale_price': Decimal('80.00'), 'cost_price': Decimal('55.00')},
            {'sku': 'PROD007', 'name': 'Impresora HP', 'category': cat_objs[4], 'brand': 'HP', 'unit_of_measure': unit_objs[0], 'sale_price': Decimal('200.00'), 'cost_price': Decimal('140.00')},
            {'sku': 'PROD008', 'name': 'Papel A4 (500 hojas)', 'category': cat_objs[4], 'brand': '', 'unit_of_measure': unit_objs[4], 'sale_price': Decimal('8.00'), 'cost_price': Decimal('5.00')},
            {'sku': 'PROD009', 'name': 'Silla de oficina', 'category': cat_objs[3], 'brand': '', 'unit_of_measure': unit_objs[0], 'sale_price': Decimal('180.00'), 'cost_price': Decimal('120.00')},
            {'sku': 'PROD010', 'name': 'Escritorio ejecutivo', 'category': cat_objs[3], 'brand': '', 'unit_of_measure': unit_objs[0], 'sale_price': Decimal('350.00'), 'cost_price': Decimal('250.00')},
        ]
        for prod in products:
            Product.objects.get_or_create(sku=prod['sku'], defaults=prod)
        
        self.stdout.write(self.style.SUCCESS('  ✓ Inventario creado'))

    def create_hr_data(self):
        """Crear datos de recursos humanos"""
        from apps.hr.models import Department, Position, Employee
        
        self.stdout.write('  - Creando departamentos...')
        departments = [
            {'code': 'DIR', 'name': 'Dirección General'},
            {'code': 'VENTAS', 'name': 'Ventas'},
            {'code': 'COMPRAS', 'name': 'Compras'},
            {'code': 'FINANZAS', 'name': 'Finanzas'},
            {'code': 'RRHH', 'name': 'Recursos Humanos'},
            {'code': 'TI', 'name': 'Tecnología'},
            {'code': 'ALMACEN', 'name': 'Almacén'},
        ]
        dept_objs = []
        for dept in departments:
            obj, _ = Department.objects.get_or_create(code=dept['code'], defaults=dept)
            dept_objs.append(obj)
        
        self.stdout.write('  - Creando posiciones...')
        positions = [
            {'code': 'GER', 'name': 'Gerente General', 'department': dept_objs[0], 'min_salary': Decimal('5000'), 'max_salary': Decimal('10000')},
            {'code': 'JVEN', 'name': 'Jefe de Ventas', 'department': dept_objs[1], 'min_salary': Decimal('3000'), 'max_salary': Decimal('5000')},
            {'code': 'VEND', 'name': 'Vendedor', 'department': dept_objs[1], 'min_salary': Decimal('1500'), 'max_salary': Decimal('2500')},
            {'code': 'JCOM', 'name': 'Jefe de Compras', 'department': dept_objs[2], 'min_salary': Decimal('3000'), 'max_salary': Decimal('5000')},
            {'code': 'COMP', 'name': 'Comprador', 'department': dept_objs[2], 'min_salary': Decimal('1500'), 'max_salary': Decimal('2500')},
            {'code': 'CONT', 'name': 'Contador', 'department': dept_objs[3], 'min_salary': Decimal('2500'), 'max_salary': Decimal('4000')},
            {'code': 'JRRHH', 'name': 'Jefe de RRHH', 'department': dept_objs[4], 'min_salary': Decimal('3000'), 'max_salary': Decimal('5000')},
            {'code': 'PROG', 'name': 'Programador', 'department': dept_objs[5], 'min_salary': Decimal('2000'), 'max_salary': Decimal('4000')},
            {'code': 'ALMC', 'name': 'Almacenero', 'department': dept_objs[6], 'min_salary': Decimal('1200'), 'max_salary': Decimal('1800')},
        ]
        pos_objs = []
        for pos in positions:
            obj, _ = Position.objects.get_or_create(code=pos['code'], defaults=pos)
            pos_objs.append(obj)
        
        self.stdout.write('  - Creando empleados...')
        employees = [
            {'employee_code': 'EMP001', 'first_name': 'Carlos', 'last_name': 'Rodríguez', 'id_number': '12345678', 'email': 'carlos.rodriguez@erp.local', 'department': dept_objs[0], 'position': pos_objs[0], 'hire_date': date(2020, 1, 15), 'salary': Decimal('8000')},
            {'employee_code': 'EMP002', 'first_name': 'María', 'last_name': 'González', 'id_number': '23456789', 'email': 'maria.gonzalez@erp.local', 'department': dept_objs[1], 'position': pos_objs[1], 'hire_date': date(2020, 3, 1), 'salary': Decimal('4000')},
            {'employee_code': 'EMP003', 'first_name': 'Juan', 'last_name': 'Pérez', 'id_number': '34567890', 'email': 'juan.perez@erp.local', 'department': dept_objs[1], 'position': pos_objs[2], 'hire_date': date(2021, 6, 15), 'salary': Decimal('2000')},
            {'employee_code': 'EMP004', 'first_name': 'Ana', 'last_name': 'Martínez', 'id_number': '45678901', 'email': 'ana.martinez@erp.local', 'department': dept_objs[2], 'position': pos_objs[3], 'hire_date': date(2020, 5, 10), 'salary': Decimal('3500')},
            {'employee_code': 'EMP005', 'first_name': 'Luis', 'last_name': 'Sánchez', 'id_number': '56789012', 'email': 'luis.sanchez@erp.local', 'department': dept_objs[3], 'position': pos_objs[5], 'hire_date': date(2019, 11, 20), 'salary': Decimal('3200')},
            {'employee_code': 'EMP006', 'first_name': 'Elena', 'last_name': 'López', 'id_number': '67890123', 'email': 'elena.lopez@erp.local', 'department': dept_objs[4], 'position': pos_objs[6], 'hire_date': date(2020, 2, 1), 'salary': Decimal('3800')},
            {'employee_code': 'EMP007', 'first_name': 'Pedro', 'last_name': 'García', 'id_number': '78901234', 'email': 'pedro.garcia@erp.local', 'department': dept_objs[5], 'position': pos_objs[7], 'hire_date': date(2021, 9, 1), 'salary': Decimal('2800')},
            {'employee_code': 'EMP008', 'first_name': 'Laura', 'last_name': 'Díaz', 'id_number': '89012345', 'email': 'laura.diaz@erp.local', 'department': dept_objs[6], 'position': pos_objs[8], 'hire_date': date(2022, 1, 10), 'salary': Decimal('1500')},
        ]
        for emp in employees:
            Employee.objects.get_or_create(employee_code=emp['employee_code'], defaults=emp)
        
        self.stdout.write(self.style.SUCCESS('  ✓ Recursos Humanos creado'))

    def create_finance_data(self):
        """Crear datos de finanzas"""
        from apps.finance.models import AccountType, Account, AccountingPeriod
        
        self.stdout.write('  - Creando tipos de cuenta...')
        account_types = [
            {'name': 'Activo', 'nature': 'asset', 'debit_nature': True},
            {'name': 'Pasivo', 'nature': 'liability', 'debit_nature': False},
            {'name': 'Patrimonio', 'nature': 'equity', 'debit_nature': False},
            {'name': 'Ingreso', 'nature': 'income', 'debit_nature': False},
            {'name': 'Gasto', 'nature': 'expense', 'debit_nature': True},
        ]
        type_objs = []
        for at in account_types:
            obj, _ = AccountType.objects.get_or_create(name=at['name'], defaults=at)
            type_objs.append(obj)
        
        self.stdout.write('  - Creando cuentas contables...')
        accounts = [
            {'code': '1', 'name': 'ACTIVO', 'account_type': type_objs[0], 'level': 1, 'is_detail': False},
            {'code': '11', 'name': 'Activo Corriente', 'account_type': type_objs[0], 'level': 2, 'is_detail': False},
            {'code': '1101', 'name': 'Caja', 'account_type': type_objs[0], 'level': 3, 'is_detail': True},
            {'code': '1102', 'name': 'Bancos', 'account_type': type_objs[0], 'level': 3, 'is_detail': True},
            {'code': '1103', 'name': 'Cuentas por Cobrar', 'account_type': type_objs[0], 'level': 3, 'is_detail': True},
            {'code': '1104', 'name': 'Inventarios', 'account_type': type_objs[0], 'level': 3, 'is_detail': True},
            {'code': '2', 'name': 'PASIVO', 'account_type': type_objs[1], 'level': 1, 'is_detail': False},
            {'code': '21', 'name': 'Pasivo Corriente', 'account_type': type_objs[1], 'level': 2, 'is_detail': False},
            {'code': '2101', 'name': 'Cuentas por Pagar', 'account_type': type_objs[1], 'level': 3, 'is_detail': True},
            {'code': '2102', 'name': 'Impuestos por Pagar', 'account_type': type_objs[1], 'level': 3, 'is_detail': True},
            {'code': '3', 'name': 'PATRIMONIO', 'account_type': type_objs[2], 'level': 1, 'is_detail': False},
            {'code': '31', 'name': 'Capital', 'account_type': type_objs[2], 'level': 2, 'is_detail': True},
            {'code': '32', 'name': 'Utilidades Retenidas', 'account_type': type_objs[2], 'level': 2, 'is_detail': True},
            {'code': '4', 'name': 'INGRESOS', 'account_type': type_objs[3], 'level': 1, 'is_detail': False},
            {'code': '41', 'name': 'Ingresos por Ventas', 'account_type': type_objs[3], 'level': 2, 'is_detail': True},
            {'code': '5', 'name': 'GASTOS', 'account_type': type_objs[4], 'level': 1, 'is_detail': False},
            {'code': '51', 'name': 'Costo de Ventas', 'account_type': type_objs[4], 'level': 2, 'is_detail': True},
            {'code': '52', 'name': 'Gastos Administrativos', 'account_type': type_objs[4], 'level': 2, 'is_detail': True},
            {'code': '53', 'name': 'Gastos de Ventas', 'account_type': type_objs[4], 'level': 2, 'is_detail': True},
        ]
        for acc in accounts:
            Account.objects.get_or_create(code=acc['code'], defaults=acc)
        
        self.stdout.write('  - Creando períodos contables...')
        today = date.today()
        AccountingPeriod.objects.get_or_create(
            code=str(today.year),
            defaults={
                'name': f'Ejercicio {today.year}',
                'start_date': date(today.year, 1, 1),
                'end_date': date(today.year, 12, 31),
                'status': 'open',
                'is_current': True
            }
        )
        
        self.stdout.write(self.style.SUCCESS('  ✓ Finanzas creado'))

    def create_sales_data(self):
        """Crear datos de ventas"""
        from apps.sales.models import CustomerGroup, Customer
        
        self.stdout.write('  - Creando grupos de clientes...')
        groups = [
            {'code': 'GEN', 'name': 'General', 'discount_percentage': Decimal('0')},
            {'code': 'VIP', 'name': 'VIP', 'discount_percentage': Decimal('10')},
            {'code': 'CORP', 'name': 'Corporativo', 'discount_percentage': Decimal('15')},
            {'code': 'MAY', 'name': 'Mayorista', 'discount_percentage': Decimal('20')},
        ]
        group_objs = []
        for grp in groups:
            obj, _ = CustomerGroup.objects.get_or_create(code=grp['code'], defaults=grp)
            group_objs.append(obj)
        
        self.stdout.write('  - Creando clientes...')
        customers = [
            {'code': 'CLI001', 'name': 'Empresa ABC S.A.', 'trade_name': 'ABC', 'tax_id': '12345678901', 'customer_type': 'company', 'group': group_objs[2], 'email': 'contacto@abc.com', 'phone': '555-1234', 'credit_limit': Decimal('50000')},
            {'code': 'CLI002', 'name': 'Juan García Pérez', 'tax_id': '87654321', 'customer_type': 'individual', 'group': group_objs[0], 'email': 'juan.garcia@email.com', 'phone': '555-5678', 'credit_limit': Decimal('5000')},
            {'code': 'CLI003', 'name': 'Comercial XYZ Ltda.', 'trade_name': 'XYZ', 'tax_id': '11223344556', 'customer_type': 'company', 'group': group_objs[3], 'email': 'ventas@xyz.com', 'phone': '555-9012', 'credit_limit': Decimal('100000')},
            {'code': 'CLI004', 'name': 'María López', 'tax_id': '22334455', 'customer_type': 'individual', 'group': group_objs[1], 'email': 'maria.lopez@email.com', 'phone': '555-3456', 'credit_limit': Decimal('10000')},
            {'code': 'CLI005', 'name': 'Tech Solutions Inc.', 'trade_name': 'TechSol', 'tax_id': '99887766554', 'customer_type': 'company', 'group': group_objs[2], 'email': 'info@techsol.com', 'phone': '555-7890', 'credit_limit': Decimal('75000')},
        ]
        for cust in customers:
            Customer.objects.get_or_create(code=cust['code'], defaults=cust)
        
        self.stdout.write(self.style.SUCCESS('  ✓ Ventas creado'))

    def create_purchasing_data(self):
        """Crear datos de compras"""
        from apps.purchasing.models import SupplierCategory, Supplier
        
        self.stdout.write('  - Creando categorías de proveedores...')
        categories = [
            {'code': 'TECH', 'name': 'Tecnología', 'description': 'Proveedores de equipos tecnológicos'},
            {'code': 'OFIC', 'name': 'Suministros de Oficina', 'description': 'Papelería y suministros'},
            {'code': 'SERV', 'name': 'Servicios', 'description': 'Proveedores de servicios'},
        ]
        cat_objs = []
        for cat in categories:
            obj, _ = SupplierCategory.objects.get_or_create(code=cat['code'], defaults=cat)
            cat_objs.append(obj)
        
        self.stdout.write('  - Creando proveedores...')
        suppliers = [
            {'code': 'PROV001', 'name': 'Distribuidora Tech', 'trade_name': 'DistriTech', 'tax_id': '20123456789', 'supplier_type': 'goods', 'category': cat_objs[0], 'email': 'ventas@distritech.com', 'phone': '555-1111'},
            {'code': 'PROV002', 'name': 'Importadora Global', 'trade_name': 'ImpoGlobal', 'tax_id': '20987654321', 'supplier_type': 'goods', 'category': cat_objs[0], 'email': 'sales@impoglobal.com', 'phone': '555-2222'},
            {'code': 'PROV003', 'name': 'Papelera Nacional', 'trade_name': 'PapelNac', 'tax_id': '20111222333', 'supplier_type': 'goods', 'category': cat_objs[1], 'email': 'pedidos@papelnac.com', 'phone': '555-3333'},
            {'code': 'PROV004', 'name': 'Servicios Integrales S.A.', 'trade_name': 'ServInt', 'tax_id': '20444555666', 'supplier_type': 'services', 'category': cat_objs[2], 'email': 'contacto@servint.com', 'phone': '555-4444'},
        ]
        for supp in suppliers:
            Supplier.objects.get_or_create(code=supp['code'], defaults=supp)
        
        self.stdout.write(self.style.SUCCESS('  ✓ Compras creado'))
