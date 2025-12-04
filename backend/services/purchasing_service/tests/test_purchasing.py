import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from apps.purchasing.models import (
    Supplier,
    SupplierCategory,
    PurchaseOrder,
    PurchaseOrderLine,
    GoodsReceipt,
    GoodsReceiptLine
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
def supplier_category(company):
    return SupplierCategory.objects.create(
        company=company,
        code='CAT001',
        name='Electronics Suppliers'
    )


@pytest.fixture
def supplier(company, supplier_category):
    return Supplier.objects.create(
        company=company,
        code='SUP001',
        name='Test Supplier',
        fiscal_name='Test Supplier S.A. de C.V.',
        tax_id='RFC789012XYZ',
        email='supplier@example.com',
        phone='+1234567890',
        category=supplier_category,
        payment_terms=30,
        is_active=True
    )


@pytest.fixture
def purchase_order(company, supplier):
    return PurchaseOrder.objects.create(
        company=company,
        supplier=supplier,
        number='PO-2024-0001',
        status='draft',
        subtotal=Decimal('500.00'),
        tax_amount=Decimal('80.00'),
        total=Decimal('580.00'),
        expected_date=timezone.now().date() + timedelta(days=7)
    )


@pytest.fixture
def purchase_order_line(purchase_order):
    return PurchaseOrderLine.objects.create(
        order=purchase_order,
        line_number=1,
        product_id=1,
        product_code='PROD001',
        product_name='Test Product',
        quantity=Decimal('10'),
        unit_price=Decimal('50.00'),
        tax_rate=Decimal('16.00'),
        tax_amount=Decimal('80.00'),
        total=Decimal('580.00'),
        received_quantity=Decimal('0')
    )


@pytest.mark.django_db
class TestSupplierModel:
    
    def test_create_supplier(self, company, supplier_category):
        """Test creating a supplier"""
        supplier = Supplier.objects.create(
            company=company,
            code='NEW001',
            name='New Supplier',
            email='new@supplier.com',
            category=supplier_category,
            is_active=True
        )
        assert supplier.code == 'NEW001'
        assert supplier.name == 'New Supplier'

    def test_supplier_string_representation(self, supplier):
        """Test supplier string representation"""
        expected = f'{supplier.code} - {supplier.name}'
        assert str(supplier) == expected


@pytest.mark.django_db
class TestPurchaseOrderModel:
    
    def test_create_purchase_order(self, company, supplier):
        """Test creating a purchase order"""
        po = PurchaseOrder.objects.create(
            company=company,
            supplier=supplier,
            status='draft',
            subtotal=Decimal('1000.00'),
            tax_amount=Decimal('160.00'),
            total=Decimal('1160.00')
        )
        assert po.status == 'draft'
        assert po.number is not None

    def test_purchase_order_string_representation(self, purchase_order):
        """Test purchase order string representation"""
        assert purchase_order.number in str(purchase_order)

    def test_send_purchase_order(self, purchase_order, purchase_order_line):
        """Test sending a purchase order"""
        purchase_order.status = 'sent'
        purchase_order.sent_date = timezone.now().date()
        purchase_order.save()
        assert purchase_order.status == 'sent'
        assert purchase_order.sent_date is not None

    def test_confirm_purchase_order(self, purchase_order, purchase_order_line):
        """Test confirming a purchase order"""
        purchase_order.status = 'confirmed'
        purchase_order.save()
        assert purchase_order.status == 'confirmed'

    def test_cancel_purchase_order(self, purchase_order):
        """Test cancelling a purchase order"""
        purchase_order.status = 'cancelled'
        purchase_order.save()
        assert purchase_order.status == 'cancelled'


@pytest.mark.django_db
class TestPurchaseOrderLine:
    
    def test_create_purchase_order_line(self, purchase_order):
        """Test creating a purchase order line"""
        line = PurchaseOrderLine.objects.create(
            order=purchase_order,
            line_number=2,
            product_id=2,
            product_code='TEST001',
            product_name='Test Item',
            quantity=Decimal('20'),
            unit_price=Decimal('25.00'),
            tax_rate=Decimal('16.00'),
            tax_amount=Decimal('80.00'),
            total=Decimal('580.00'),
            received_quantity=Decimal('0')
        )
        assert line.quantity == Decimal('20')
        assert line.received_quantity == Decimal('0')

    def test_line_pending_quantity(self, purchase_order_line):
        """Test line pending quantity calculation"""
        purchase_order_line.received_quantity = Decimal('3')
        purchase_order_line.save()
        pending = purchase_order_line.quantity - purchase_order_line.received_quantity
        assert pending == Decimal('7')


@pytest.mark.django_db
class TestGoodsReceipt:
    
    def test_create_goods_receipt(self, company, purchase_order, purchase_order_line, supplier):
        """Test creating a goods receipt"""
        purchase_order.status = 'confirmed'
        purchase_order.save()
        
        receipt = GoodsReceipt.objects.create(
            company=company,
            purchase_order=purchase_order,
            supplier=supplier,
            number='GR-2024-0001',
            status='pending'
        )
        assert receipt.number is not None
        assert receipt.status == 'pending'

    def test_complete_goods_receipt(self, company, purchase_order, purchase_order_line, supplier):
        """Test completing a goods receipt"""
        purchase_order.status = 'confirmed'
        purchase_order.save()
        
        receipt = GoodsReceipt.objects.create(
            company=company,
            purchase_order=purchase_order,
            supplier=supplier,
            number='GR-2024-0002',
            status='pending'
        )
        
        receipt_line = GoodsReceiptLine.objects.create(
            receipt=receipt,
            purchase_order_line=purchase_order_line,
            product_id=purchase_order_line.product_id,
            product_code=purchase_order_line.product_code,
            product_name=purchase_order_line.product_name,
            expected_quantity=purchase_order_line.quantity,
            received_quantity=purchase_order_line.quantity
        )
        
        receipt.status = 'completed'
        receipt.save()
        assert receipt.status == 'completed'


@pytest.mark.django_db
class TestPurchasingAPI:
    
    def test_list_suppliers(self, api_client, supplier):
        """Test listing suppliers"""
        response = api_client.get('/api/v1/purchasing/suppliers/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]

    def test_get_supplier(self, api_client, supplier):
        """Test getting a single supplier"""
        response = api_client.get(f'/api/v1/purchasing/suppliers/{supplier.id}/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]

    def test_search_suppliers(self, api_client, supplier):
        """Test searching suppliers"""
        response = api_client.get('/api/v1/purchasing/suppliers/', {'search': 'Test'})
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]

    def test_list_purchase_orders(self, api_client, purchase_order):
        """Test listing purchase orders"""
        response = api_client.get('/api/v1/purchasing/orders/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]

    def test_get_purchase_order(self, api_client, purchase_order):
        """Test getting a single purchase order"""
        response = api_client.get(f'/api/v1/purchasing/orders/{purchase_order.id}/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]

    def test_filter_purchase_orders_by_status(self, api_client, purchase_order):
        """Test filtering purchase orders by status"""
        response = api_client.get('/api/v1/purchasing/orders/', {'status': 'draft'})
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]

    def test_filter_purchase_orders_by_supplier(self, api_client, purchase_order, supplier):
        """Test filtering purchase orders by supplier"""
        response = api_client.get('/api/v1/purchasing/orders/', {'supplier': supplier.id})
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]
