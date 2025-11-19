from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'tipo_usuario', 'is_staff')
    
    list_filter = ('tipo_usuario', 'is_staff', 'is_superuser', 'groups')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('tipo_usuario',)}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Adicionais', {'fields': ('tipo_usuario',)}),
    )
    
    search_fields = ('email', 'first_name', 'last_name')
    
    ordering = ('email',)