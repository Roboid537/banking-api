from decimal import Decimal
from rest_framework import serializers
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User

from .models import Account, Transaction

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class AccountSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Account
        fields = ('id', 'user', 'balance')

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('id', 'account', 'amount', 'transaction_type', 'timestamp', 'description')

class CreateAccountSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    initial_balance = serializers.DecimalField(max_digits=10, decimal_places=2,  validators=[MinValueValidator(Decimal('0.00'))])

class DepositWithdrawSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])

class TransferSerializer(serializers.Serializer):
    to_account = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])