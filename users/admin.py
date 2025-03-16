from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'first_name', 'last_name', 'role', 'phone_number', 'city', 'company_name', 'taux_avance')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {
            'fields': ('first_name', 'last_name', 'phone_number', 'address', 'city', 'company_name')
        }),
        ('Paramètres annonceur', {
            'fields': ('taux_avance',),
            'classes': ('collapse',),
        }),
        ('Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'company_name', 'taux_avance', 'is_staff', 'is_superuser')
        }),
    )
    search_fields = ('email', 'first_name', 'last_name', 'city', 'company_name')
    ordering = ('email',)

# Désenregistrer l'ancien admin si nécessaire
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
