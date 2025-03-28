from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Card, Transaction, Settlement
from .serializers import (
    UserSerializer, CardSerializer, TransactionSerializer, SettlementSerializer,
    UserRegistrationSerializer, CardLinkSerializer, RechargeSerializer,
    PaymentSerializer, AnalyticsSerializer
)
import uuid

User = get_user_model()

# Web Views
def login_view(request):
    return render(request, 'login.html')

def register_view(request):
    return render(request, 'register.html')

def customer_dashboard(request):
    return render(request, 'customer_dashboard.html')

def outlet_dashboard(request):
    return render(request, 'outlet_dashboard.html')

def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

# API Views
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == User.Role.ADMIN:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.ADMIN:
            return Card.objects.all()
        return Card.objects.filter(customer=user)

    @action(detail=False, methods=['post'])
    def link_card(self, request):
        serializer = CardLinkSerializer(data=request.data)
        if serializer.is_valid():
            card_number = serializer.validated_data['card_number']
            try:
                card = Card.objects.get(card_number=card_number, customer=None)
                card.customer = request.user
                card.save()
                return Response({'message': 'Card linked successfully'})
            except Card.DoesNotExist:
                return Response(
                    {'error': 'Invalid card number or card already linked'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.ADMIN:
            return Transaction.objects.all()
        elif user.role == User.Role.OUTLET:
            return Transaction.objects.filter(outlet=user)
        return Transaction.objects.filter(customer=user)

    @action(detail=False, methods=['post'])
    def make_payment(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            card_number = serializer.validated_data['card_number']
            amount = serializer.validated_data['amount']
            outlet_id = serializer.validated_data['outlet_id']

            try:
                card = Card.objects.get(card_number=card_number, is_active=True)
                outlet = User.objects.get(id=outlet_id, role=User.Role.OUTLET)

                if card.balance < amount:
                    return Response(
                        {'error': 'Insufficient balance'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Create transaction
                transaction = Transaction.objects.create(
                    transaction_id=str(uuid.uuid4()),
                    transaction_type=Transaction.TransactionType.PAYMENT,
                    card=card,
                    customer=card.customer,
                    outlet=outlet,
                    amount=amount,
                    status='COMPLETED'
                )

                # Update balances
                card.balance -= amount
                card.save()
                outlet.balance += amount
                outlet.save()

                return Response({
                    'message': 'Payment successful',
                    'transaction_id': transaction.transaction_id
                })

            except (Card.DoesNotExist, User.DoesNotExist):
                return Response(
                    {'error': 'Invalid card or outlet'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SettlementViewSet(viewsets.ModelViewSet):
    queryset = Settlement.objects.all()
    serializer_class = SettlementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.ADMIN:
            return Settlement.objects.all()
        return Settlement.objects.filter(outlet=user)

class RegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RechargeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.user.role != User.Role.ADMIN:
            return Response(
                {'error': 'Only admin can perform recharge'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = RechargeSerializer(data=request.data)
        if serializer.is_valid():
            card_number = serializer.validated_data['card_number']
            amount = serializer.validated_data['amount']

            try:
                card = Card.objects.get(card_number=card_number, is_active=True)
                
                # Create transaction
                transaction = Transaction.objects.create(
                    transaction_id=str(uuid.uuid4()),
                    transaction_type=Transaction.TransactionType.RECHARGE,
                    card=card,
                    customer=card.customer,
                    amount=amount,
                    status='COMPLETED'
                )

                # Update balance
                card.balance += amount
                card.save()

                return Response({
                    'message': 'Recharge successful',
                    'transaction_id': transaction.transaction_id
                })

            except Card.DoesNotExist:
                return Response(
                    {'error': 'Invalid card number'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != User.Role.ADMIN:
            return Response(
                {'error': 'Only admin can view analytics'},
                status=status.HTTP_403_FORBIDDEN
            )

        analytics = {
            'total_transactions': Transaction.objects.count(),
            'total_amount': Transaction.objects.aggregate(
                total=Sum('amount'))['total'] or 0,
            'active_cards': Card.objects.filter(is_active=True).count(),
            'total_customers': User.objects.filter(
                role=User.Role.CUSTOMER).count(),
            'total_outlets': User.objects.filter(role=User.Role.OUTLET).count(),
        }

        serializer = AnalyticsSerializer(analytics)
        return Response(serializer.data)
