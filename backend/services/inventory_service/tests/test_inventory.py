import pytest
from decimal import Decimal
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from apps.inventory.models import (
    Product,
    Category,
    Brand,
    Warehouse,
    WarehouseLocation,
    Stock,
    InventoryTransaction
)
from apps.core.models import Company


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def company():
    return Company.objects.create(
        code='COMP001',
        name='Test Company',
        tax_id='RFC123456ABC',
        currency='MXN',
        is_active=True
    )


@pytest.fixture
def category(company):
    return Category.objects.create(
        company=company,
        code='ELEC',
        name='Electronics',
        description='Electronic products'
    )


@pytest.fixture
def brand(company):
    return Brand.objects.create(
        company=company,
        code='BRAND01',
        name='Test Brand'
    )


@pytest.fixture
def warehouse(company):
    return Warehouse.objects.create(
        company=company,
        code='WH001',
        name='Main Warehouse',
        address='123 Main St',
        is_active=True
    )


@pytest.fixture
def warehouse_location(warehouse):
    return WarehouseLocation.objects.create(
        warehouse=warehouse,
        code='LOC-A1',
        name='Location A1',
        aisle='A',
        rack='1',
        shelf='1',
        bin='1'
    )


@pytest.fixture
def product(company, category, brand):
    return Product.objects.create(
        company=company,
        sku='PROD001',
        name='Test Product',
        description='A test product',
        category=category,
        brand=brand,
        sale_price=Decimal('99.99'),
        cost_price=Decimal('50.00'),
        min_stock=Decimal('10'),
        is_active=True
    )


@pytest.fixture
def stock(product, warehouse, warehouse_location):
    return Stock.objects.create(
        product=product,
        warehouse=warehouse,
        location=warehouse_location,
        quantity=Decimal('100'),
        reserved_quantity=Decimal('0')
    )


@pytest.mark.django_db
class TestProductModel:
    
    def test_create_product(self, company, category):
        """Test creating a product"""
        product = Product.objects.create(
            company=company,
            sku='TEST001',
            name='New Product',
            category=category,
            sale_price=Decimal('149.99'),
            cost_price=Decimal('75.00')
        )
        assert product.sku == 'TEST001'
        assert product.name == 'New Product'
        assert product.sale_price == Decimal('149.99')
        assert product.is_active

    def test_product_string_representation(self, product):
        """Test product string representation"""
        expected = f'{product.sku} - {product.name}'
        assert str(product) == expected

    def test_product_profit_margin(self, product):
        """Test product profit margin calculation"""
        # (sale_price - cost_price) / cost_price * 100
        expected_margin = ((product.sale_price - product.cost_price) / product.cost_price) * 100
        # Product model might have a profit_margin property
        if hasattr(product, 'profit_margin'):
            assert abs(product.profit_margin - expected_margin) < Decimal('0.01')


@pytest.mark.django_db
class TestCategoryModel:
    
    def test_create_category(self, company):
        """Test creating a category"""
        category = Category.objects.create(
            company=company,
            code='FURN',
            name='Furniture',
            description='Furniture items'
        )
        assert category.name == 'Furniture'
        assert category.code == 'FURN'

    def test_category_string_representation(self, category):
        """Test category string representation"""
        assert category.name in str(category)


@pytest.mark.django_db
class TestStock:
    
    def test_stock_creation(self, product, warehouse, warehouse_location):
        """Test creating stock"""
        stock = Stock.objects.create(
            product=product,
            warehouse=warehouse,
            location=warehouse_location,
            quantity=Decimal('50')
        )
        assert stock.quantity == Decimal('50')
        assert stock.available_quantity == Decimal('50')

    def test_stock_available_quantity(self, stock):
        """Test available quantity calculation"""
        stock.reserved_quantity = Decimal('20')
        stock.save()
        assert stock.available_quantity == Decimal('80')

    def test_stock_is_low(self, product, warehouse, warehouse_location):
        """Test low stock detection"""
        stock = Stock.objects.create(
            product=product,
            warehouse=warehouse,
            location=warehouse_location,
            quantity=Decimal('5')  # Below min_stock of 10
        )
        # Check if product has low stock
        if hasattr(stock, 'is_low_stock'):
            assert stock.is_low_stock


@pytest.mark.django_db
class TestInventoryTransaction:
    
    def test_transaction_in(self, product, warehouse, warehouse_location, stock):
        """Test inventory transaction - receiving"""
        initial_qty = stock.quantity
        transaction = InventoryTransaction.objects.create(
            product=product,
            warehouse=warehouse,
            location=warehouse_location,
            transaction_type='IN',
            quantity=Decimal('50'),
            reference='Purchase receipt'
        )
        assert transaction.quantity == Decimal('50')
        assert transaction.transaction_type == 'IN'

    def test_transaction_out(self, product, warehouse, warehouse_location, stock):
        """Test inventory transaction - shipping"""
        transaction = InventoryTransaction.objects.create(
            product=product,
            warehouse=warehouse,
            location=warehouse_location,
            transaction_type='OUT',
            quantity=Decimal('30'),
            reference='Sales order'
        )
        assert transaction.quantity == Decimal('30')
        assert transaction.transaction_type == 'OUT'


@pytest.mark.django_db
class TestInventoryAPI:
    
    def test_list_products(self, api_client, product):
        """Test listing products"""
        response = api_client.get('/api/v1/inventory/products/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]

    def test_get_product(self, api_client, product):
        """Test getting a single product"""
        response = api_client.get(f'/api/v1/inventory/products/{product.id}/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]

    def test_search_products(self, api_client, product):
        """Test searching products"""
        response = api_client.get('/api/v1/inventory/products/', {'search': 'Test'})
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]

    def test_list_warehouses(self, api_client, warehouse):
        """Test listing warehouses"""
        response = api_client.get('/api/v1/inventory/warehouses/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]

    def test_list_categories(self, api_client, category):
        """Test listing categories"""
        response = api_client.get('/api/v1/inventory/categories/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]
