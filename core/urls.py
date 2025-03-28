from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'cards', views.CardViewSet)
router.register(r'transactions', views.TransactionViewSet)
router.register(r'settlements', views.SettlementViewSet)

urlpatterns = [
    # Web Views
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    path('dashboard/outlet/', views.outlet_dashboard, name='outlet_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),

    # API Endpoints
    path('api/', include(router.urls)),
    path('api/register/', views.RegistrationView.as_view(), name='api_register'),
    path('api/recharge/', views.RechargeView.as_view(), name='api_recharge'),
    path('api/analytics/', views.AnalyticsView.as_view(), name='api_analytics'),
]
