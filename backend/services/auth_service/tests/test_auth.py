import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.mark.django_db
class TestAuthEndpoints:
    
    def test_register_user(self, api_client):
        """Test user registration"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = api_client.post('/api/v1/auth/register/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert User.objects.filter(username='newuser').exists()

    def test_login_user(self, api_client, user):
        """Test user login"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = api_client.post('/api/v1/auth/login/', data)
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_login_invalid_credentials(self, api_client, user):
        """Test login with invalid credentials"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = api_client.post('/api/v1/auth/login/', data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_profile(self, authenticated_client, user):
        """Test get user profile"""
        response = authenticated_client.get('/api/v1/auth/profile/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == user.username
        assert response.data['email'] == user.email

    def test_update_profile(self, authenticated_client, user):
        """Test update user profile"""
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = authenticated_client.patch('/api/v1/auth/profile/', data)
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.first_name == 'Updated'
        assert user.last_name == 'Name'

    def test_change_password(self, authenticated_client, user):
        """Test change password"""
        data = {
            'old_password': 'testpass123',
            'new_password': 'newpass456',
            'confirm_password': 'newpass456'
        }
        response = authenticated_client.post('/api/v1/auth/change-password/', data)
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.check_password('newpass456')

    def test_refresh_token(self, api_client, user):
        """Test token refresh"""
        # First login to get tokens
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        login_response = api_client.post('/api/v1/auth/login/', login_data)
        refresh_token = login_response.data['refresh']
        
        # Now refresh the token
        response = api_client.post('/api/v1/auth/token/refresh/', {'refresh': refresh_token})
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data


@pytest.mark.django_db
class TestUserModel:
    
    def test_create_user(self):
        """Test creating a regular user"""
        user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='regularpass123'
        )
        assert user.username == 'regular'
        assert user.email == 'regular@example.com'
        assert user.check_password('regularpass123')
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser

    def test_create_superuser(self):
        """Test creating a superuser"""
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        assert admin.username == 'admin'
        assert admin.is_staff
        assert admin.is_superuser

    def test_user_string_representation(self, user):
        """Test user string representation"""
        assert str(user) == user.username

    def test_user_full_name(self, user):
        """Test user full name method"""
        assert user.get_full_name() == 'Test User'
