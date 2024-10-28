from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Account, Transaction

class AccountViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.account = Account.objects.create(user=self.user, balance=1000)
        self.client.force_authenticate(user=self.user)

    def test_create_account(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'initial_balance': '500.00'
        }
        response = self.client.post('/api/accounts/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Account.objects.count(), 2)
        new_account = Account.objects.get(user__username='newuser')
        self.assertEqual(new_account.balance, Decimal('500.00'))

    def test_deposit(self):
        data = {'amount': '200.00'}
        response = self.client.post(f'/api/accounts/{self.account.id}/deposit/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal('1200.00'))

    def test_withdraw_success(self):
        data = {'amount': '200.00'}
        response = self.client.post(f'/api/accounts/{self.account.id}/withdraw/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal('800.00'))

    def test_withdraw_insufficient_funds(self):
        data = {'amount': '1200.00'}
        response = self.client.post(f'/api/accounts/{self.account.id}/withdraw/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal('1000.00'))

    def test_transfer_success(self):
        recipient = User.objects.create_user(username='recipient', password='testpass')
        recipient_account = Account.objects.create(user=recipient, balance=500)
        data = {
            'to_account': recipient_account.id,
            'amount': '300.00'
        }
        response = self.client.post(f'/api/accounts/{self.account.id}/transfer/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.account.refresh_from_db()
        recipient_account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal('700.00'))
        self.assertEqual(recipient_account.balance, Decimal('800.00'))

    def test_transfer_insufficient_funds(self):
        recipient = User.objects.create_user(username='recipient', password='testpass')
        recipient_account = Account.objects.create(user=recipient, balance=500)
        data = {
            'to_account': recipient_account.id,
            'amount': '1200.00'
        }
        response = self.client.post(f'/api/accounts/{self.account.id}/transfer/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.account.refresh_from_db()
        recipient_account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal('1000.00'))
        self.assertEqual(recipient_account.balance, Decimal('500.00'))

    def test_transaction_history(self):
        # Create some transactions
        Transaction.objects.create(account=self.account, amount=100, transaction_type='DEPOSIT')
        Transaction.objects.create(account=self.account, amount=50, transaction_type='WITHDRAWAL')

        response = self.client.get(f'/api/accounts/{self.account.id}/transaction_history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_unauthorized_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/accounts/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_account_details(self):
        response = self.client.get(f'/api/accounts/{self.account.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['balance'], '1000.00')

    def test_list_accounts(self):
        response = self.client.get('/api/accounts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_account_invalid_data(self):
        data = {
            'username': 'newuser',
            'email': 'invalid-email',
            'initial_balance': '-100.00'
        }
        response = self.client.post('/api/accounts/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_deposit_negative_amount(self):
        data = {'amount': '-200.00'}
        response = self.client.post(f'/api/accounts/{self.account.id}/deposit/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_withdraw_negative_amount(self):
        data = {'amount': '-200.00'}
        response = self.client.post(f'/api/accounts/{self.account.id}/withdraw/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_transfer_to_non_existent_account(self):
        data = {
            'to_account': 9999,  # Non-existent account ID
            'amount': '300.00'
        }
        response = self.client.post(f'/api/accounts/{self.account.id}/transfer/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)