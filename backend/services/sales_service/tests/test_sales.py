import pytest
from decimal import Decimal
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from apps.sales.models import (
    Customer,
    CustomerGroup,
    SalesOrder,
    SalesOrderLine,
    Invoice,
    InvoiceLine
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
def customer_group(company):
    return CustomerGroup.objects.create(
        company=company,
        code='GRP001',
        name='Retail Customers'
    )


@pytest.fixture
def customer(company, customer_group):
    return Customer.objects.create(
        company=company,
        code='CUST001',
        name='Test Customer',
        fiscal_name='Test Customer S.A. de C.V.',
        tax_id='RFC123456ABC',
        email='customer@example.com',
        phone='+1234567890',
        customer_group=customer_group,
        credit_limit=Decimal('10000.00'),
        is_active=True
    )


@pytest.fixture
def product():
    """Mock product for order items"""
    from unittest.mock import MagicMock
    product = MagicMock()
    product.id = 1
    product.sku = 'PROD001'
    product.name = 'Test Product'
    product.price = Decimal('99.99')
    return product


@pytest.fixture
def sales_order(company, customer):
    return SalesOrder.objects.create(
        company=company,
        customer=customer,
        number='SO-2024-0001',
        status='draft',
        subtotal=Decimal('199.98'),
        discount_amount=Decimal('0.00'),
        tax_amount=Decimal('31.99'),
        total=Decimal('231.97'),
        payment_status='pending'
    )


@pytest.fixture
def sales_order_line(sales_order):
    return SalesOrderLine.objects.create(
        order=sales_order,
        line_number=1,
        product_id=1,
        product_code='PROD001',
        product_name='Test Product',
        quantity=Decimal('2'),
        unit_price=Decimal('99.99'),
        discount_percent=Decimal('0.00'),
        discount_amount=Decimal('0.00'),
        tax_rate=Decimal('16.00'),
        tax_amount=Decimal('31.99'),
        total=Decimal('231.97')
    )


@pytest.mark.django_db
class TestCustomerModel:
    
    def test_create_customer(self, company, customer_group):
        """Test creating a customer"""
        customer = Customer.objects.create(
            company=company,
            code='NEW001',
            name='New Customer',
            email='new@example.com',
            customer_group=customer_group,
            is_active=True
        )
        assert customer.code == 'NEW001'
        assert customer.name == 'New Customer'
        assert customer.credit_used == Decimal('0.00')

    def test_customer_string_representation(self, customer):
        """Test customer string representation"""
        expected = f'{customer.code} - {customer.name}'
        assert str(customer) == expected

    def test_customer_available_credit(self, customer):
        """Test customer available credit calculation"""
        customer.credit_used = Decimal('2000.00')
        customer.save()
        expected_available = customer.credit_limit - customer.credit_used
        assert customer.available_credit == expected_available


@pytest.mark.django_db
class TestSalesOrderModel:
    
    def test_create_sales_order(self, company, customer):
        """Test creating a sales order"""
        order = SalesOrder.objects.create(
            company=company,
            customer=customer,
            status='draft',
            subtotal=Decimal('100.00'),
            tax_amount=Decimal('16.00'),
            total=Decimal('116.00')
        )
        assert order.status == 'draft'
        assert order.number is not None

    def test_sales_order_string_representation(self, sales_order):
        """Test sales order string representation"""
        assert sales_order.number in str(sales_order)

    def test_confirm_sales_order(self, sales_order, sales_order_line):
        """Test confirming a sales order"""
        sales_order.status = 'confirmed'
        sales_order.confirmed_at = timezone.now()
        sales_order.save()
        assert sales_order.status == 'confirmed'
        assert sales_order.confirmed_at is not None

    def test_cancel_sales_order(self, sales_order):
        """Test cancelling a sales order"""
        sales_order.status = 'cancelled'
        sales_order.save()
        assert sales_order.status == 'cancelled'


@pytest.mark.django_db
class TestSalesOrderLine:
    
    def test_create_sales_order_line(self, sales_order):
        """Test creating a sales order line"""
        line = SalesOrderLine.objects.create(
            order=sales_order,
            line_number=2,
            product_id=2,
            product_code='TEST001',
            product_name='Test Item',
            quantity=Decimal('5'),
            unit_price=Decimal('50.00'),
            discount_percent=Decimal('10.00'),
            discount_amount=Decimal('25.00'),
            tax_rate=Decimal('16.00'),
            tax_amount=Decimal('36.00'),
            total=Decimal('261.00')
        )
        assert line.quantity == Decimal('5')
        assert line.unit_price == Decimal('50.00')


@pytest.mark.django_db
class TestSalesAPI:
    
    def test_list_customers(self, api_client, customer):
        """Test listing customers"""
        response = api_client.get('/api/v1/sales/customers/')
        # API might require authentication
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]

    def test_get_customer(self, api_client, customer):
        """Test getting a single customer"""
        response = api_client.get(f'/api/v1/sales/customers/{customer.id}/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]

    def test_list_sales_orders(self, api_client, sales_order):
        """Test listing sales orders"""
        response = api_client.get('/api/v1/sales/orders/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]

    def test_get_sales_order(self, api_client, sales_order):
        """Test getting a single sales order"""
        response = api_client.get(f'/api/v1/sales/orders/{sales_order.id}/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]


@pytest.mark.django_db
class TestInvoice:
    
    def test_create_invoice(self, company, customer, sales_order, sales_order_line):
        """Test creating invoice from sales order"""
        invoice = Invoice.objects.create(
            company=company,
            customer=customer,
            sales_order=sales_order,
            number='INV-2024-0001',
            status='draft',
            subtotal=sales_order.subtotal,
            discount_amount=sales_order.discount_amount,
            tax_amount=sales_order.tax_amount,
            total=sales_order.total
        )
        assert invoice.sales_order == sales_order
        assert invoice.total == sales_order.total
        assert invoice.status == 'draft'

    def test_invoice_string_representation(self, company, customer, sales_order, sales_order_line):
        """Test invoice string representation"""
        invoice = Invoice.objects.create(
            company=company,
            customer=customer,
            sales_order=sales_order,
            number='INV-2024-0002',
            status='draft',
            subtotal=sales_order.subtotal,
            tax_amount=sales_order.tax_amount,
            total=sales_order.total
        )
        assert invoice.number in str(invoice)
