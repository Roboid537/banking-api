
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import transaction
from django.contrib.auth.models import User
from .models import Account, Transaction
from .serializers import (
    AccountSerializer, TransactionSerializer, CreateAccountSerializer,
    DepositWithdrawSerializer, TransferSerializer
)

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    http_method_names = ['get', 'post', 'head']


    def get_serializer_class(self):

        if self.action in ['deposit', 'withdraw']:
            return DepositWithdrawSerializer

        elif self.action == 'transaction_history':
            return TransactionSerializer

        elif self.action == 'transfer':
            return TransferSerializer

        elif self.request.method in ['POST', 'PUT', 'PATCH']:
            return CreateAccountSerializer

        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = CreateAccountSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                user = User.objects.create_user(
                    username=serializer.validated_data['username'],
                    email=serializer.validated_data['email']
                )
                account = Account.objects.create(
                    user=user,
                    balance=serializer.validated_data['initial_balance']
                )
                Transaction.objects.create(
                    account=account,
                    amount=serializer.validated_data['initial_balance'],
                    transaction_type='DEPOSIT',
                    description='Initial deposit'
                )
            return Response(AccountSerializer(account).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def deposit(self, request, pk=None):
        account = self.get_object()
        serializer = DepositWithdrawSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            with transaction.atomic():
                account.balance += amount
                account.save()
                Transaction.objects.create(
                    account=account,
                    amount=amount,
                    transaction_type='DEPOSIT',
                    description='Deposit'
                )
            return Response(AccountSerializer(account).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        account = self.get_object()
        serializer = DepositWithdrawSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            if account.balance >= amount:
                with transaction.atomic():
                    account.balance -= amount
                    account.save()
                    Transaction.objects.create(
                        account=account,
                        amount=amount,
                        transaction_type='WITHDRAWAL',
                        description='Withdrawal'
                    )
                return Response(AccountSerializer(account).data)
            return Response({'error': 'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def transfer(self, request, pk=None):
        from_account = self.get_object()
        serializer = TransferSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            to_account_id = serializer.validated_data['to_account']
            try:
                to_account = Account.objects.get(id=to_account_id)
            except Account.DoesNotExist:
                return Response({'error': 'Recipient account not found'}, status=status.HTTP_404_NOT_FOUND)

            if from_account.balance >= amount:
                with transaction.atomic():
                    from_account.balance -= amount
                    to_account.balance += amount
                    from_account.save()
                    to_account.save()
                    Transaction.objects.create(
                        account=from_account,
                        amount=amount,
                        transaction_type='TRANSFER',
                        description=f'Transfer to account {to_account_id}'
                    )
                    Transaction.objects.create(
                        account=to_account,
                        amount=amount,
                        transaction_type='TRANSFER',
                        description=f'Transfer from account {from_account.id}'
                    )
                return Response(AccountSerializer(from_account).data)
            return Response({'error': 'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def transaction_history(self, request, pk=None):
        account = self.get_object()
        transactions = Transaction.objects.filter(account=account).order_by('-timestamp')
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)