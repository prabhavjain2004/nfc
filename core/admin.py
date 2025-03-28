from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Card, Transaction, Settlement

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'balance', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Additional info', {'fields': ('role', 'phone_number', 'address', 'balance')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('card_number', 'customer', 'balance', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('card_number', 'customer__username')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('card_number', 'customer')}),
        ('Status', {'fields': ('is_active', 'balance')}),
    )

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'transaction_type', 'customer', 'outlet', 
                   'amount', 'status', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('transaction_id', 'customer__username', 'outlet__username')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('transaction_id', 'transaction_type')}),
        ('Details', {'fields': ('card', 'customer', 'outlet', 'amount')}),
        ('Status', {'fields': ('status',)}),
    )
    
    readonly_fields = ('transaction_id', 'created_at')

@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
    list_display = ('outlet', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('outlet__username',)
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('outlet', 'amount')}),
        ('Status', {'fields': ('status',)}),
        ('Transactions', {'fields': ('transactions',)}),
    )
    
    filter_horizontal = ('transactions',)
