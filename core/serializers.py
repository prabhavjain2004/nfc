from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Card, Transaction, Settlement

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'role', 'phone_number', 
                 'address', 'balance', 'first_name', 'last_name')
        read_only_fields = ('balance',)

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ('id', 'card_number', 'customer', 'is_active', 'balance', 
                 'created_at', 'updated_at')
        read_only_fields = ('balance', 'created_at', 'updated_at')

class TransactionSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.username', read_only=True)
    outlet_name = serializers.CharField(source='outlet.username', read_only=True)
    card_number = serializers.CharField(source='card.card_number', read_only=True)

    class Meta:
        model = Transaction
        fields = ('id', 'transaction_id', 'transaction_type', 'card', 'customer',
                 'customer_name', 'outlet', 'outlet_name', 'card_number', 'amount',
                 'status', 'created_at', 'updated_at')
        read_only_fields = ('transaction_id', 'created_at', 'updated_at')

class SettlementSerializer(serializers.ModelSerializer):
    outlet_name = serializers.CharField(source='outlet.username', read_only=True)
    transactions = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Settlement
        fields = ('id', 'outlet', 'outlet_name', 'amount', 'status', 
                 'transactions', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'confirm_password', 'role',
                 'phone_number', 'address', 'first_name', 'last_name')

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class CardLinkSerializer(serializers.Serializer):
    card_number = serializers.CharField()

class RechargeSerializer(serializers.Serializer):
    card_number = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

class PaymentSerializer(serializers.Serializer):
    card_number = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    outlet_id = serializers.IntegerField()

class AnalyticsSerializer(serializers.Serializer):
    total_transactions = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    active_cards = serializers.IntegerField()
    total_customers = serializers.IntegerField()
    total_outlets = serializers.IntegerField()
