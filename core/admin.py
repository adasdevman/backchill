from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.contrib import messages
from django import forms
from users.models import User, Preference
from .models import (
    Annonce,
    Categorie,
    SousCategorie,
    Horaire,
    Tarif,
    GaleriePhoto,
    Payment,
    Notification
)
from django.urls import reverse
import uuid

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'get_phone_number', 'role', 'first_name', 'last_name', 'get_date_joined', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'role', 'date_joined')
    ordering = ('-date_joined',)
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'phone_number', 'role', 'profile_image', 'banner_image')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'phone_number', 'role'),
        }),
    )

    def get_phone_number(self, obj):
        return obj.phone_number if obj.phone_number else "Non renseigné"
    get_phone_number.short_description = "Téléphone"

    def get_date_joined(self, obj):
        return obj.date_joined.strftime("%d/%m/%Y %H:%M")
    get_date_joined.short_description = "Date d'inscription"

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'ordre')
    search_fields = ('nom',)

@admin.register(SousCategorie)
class SousCategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'categorie', 'ordre')
    list_filter = ('categorie',)
    search_fields = ('nom',)

class HoraireInline(admin.TabularInline):
    model = Horaire
    extra = 1

class TarifInline(admin.TabularInline):
    model = Tarif
    extra = 1

class GaleriePhotoInline(admin.TabularInline):
    model = GaleriePhoto
    extra = 1

@admin.register(Annonce)
class AnnonceAdmin(admin.ModelAdmin):
    list_display = ('titre', 'categorie', 'sous_categorie', 'utilisateur', 'est_actif', 'status', 'created')
    list_filter = ('categorie', 'sous_categorie', 'est_actif', 'status')
    search_fields = ('titre', 'description', 'localisation')
    readonly_fields = ('created', 'modified')
    fieldsets = (
        ('Informations principales', {
            'fields': ('titre', 'description', 'localisation', 'utilisateur')
        }),
        ('Catégorisation', {
            'fields': ('categorie', 'sous_categorie')
        }),
        ('État', {
            'fields': ('est_actif', 'status', 'date_evenement')
        }),
        ('Métadonnées', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'amount', 'status', 'payment_type', 'created')
    list_filter = ('status', 'payment_type', 'created')
    search_fields = ('transaction_id', 'user__email', 'annonce_titre')
    readonly_fields = ('transaction_id', 'created', 'modified')
    fieldsets = (
        ('Informations principales', {
            'fields': ('transaction_id', 'user', 'amount', 'status', 'payment_type', 'description')
        }),
        ('Informations utilisateur', {
            'fields': ('user_first_name', 'user_last_name', 'user_email', 'user_phone', 'user_address', 'user_city')
        }),
        ('Informations annonce', {
            'fields': ('annonce', 'annonce_titre', 'annonce_categorie', 'annonce_sous_categorie', 'annonce_utilisateur_id')
        }),
        ('Informations tarif', {
            'fields': ('tarif', 'tarif_nom', 'tarif_prix')
        }),
        ('Dates', {
            'fields': ('created', 'modified')
        }),
    )

    def get_annonce_title(self, obj):
        if obj.annonce:
            return format_html('<a href="{}">{}</a>',
                reverse('admin:core_annonce_change', args=[obj.annonce.id]),
                obj.annonce.titre)
        return "N/A"
    get_annonce_title.short_description = "Annonce"

    def save_model(self, request, obj, form, change):
        if not obj.transaction_id:
            obj.transaction_id = f"TR-{str(uuid.uuid4())[:8]}"
        super().save_model(request, obj, form, change)

class NotificationForm(forms.ModelForm):
    TARGET_CHOICES = [
        ('single', 'Un seul utilisateur'),
        ('all', 'Tous les rôles confondus'),
        ('users', 'Tous les utilisateurs (role UTILISATEUR)'),
        ('advertisers', 'Tous les annonceurs (role ANNONCEUR)'),
        ('admin', 'Tous les administrateurs (role ADMIN)'),
        ('staff', 'Staff uniquement')
    ]
    
    target_type = forms.ChoiceField(
        choices=TARGET_CHOICES,
        label="Type de destinataire",
        widget=forms.RadioSelect,
        initial='single'
    )
    
    class Meta:
        model = Notification
        fields = ['title', 'message', 'user']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].required = False
        self.fields['user'].label = "Utilisateur spécifique (uniquement si 'Un seul utilisateur' est sélectionné)"

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    form = NotificationForm
    list_display = ['user', 'title', 'message', 'is_read', 'created']
    list_filter = ['is_read', 'created']
    search_fields = ['title', 'message', 'user__email']
    readonly_fields = ['created', 'modified']
    ordering = ['-created']

    def save_model(self, request, obj, form, change):
        target_type = form.cleaned_data.get('target_type')
        title = form.cleaned_data.get('title')
        message = form.cleaned_data.get('message')
        
        if target_type == 'single':
            if not form.cleaned_data.get('user'):
                messages.error(request, "Veuillez sélectionner un utilisateur pour l'envoi individuel.")
                return
            super().save_model(request, obj, form, change)
        else:
            # Ne pas sauvegarder le modèle original pour les envois multiples
            users = []
            if target_type == 'all':
                users = User.objects.all()  # Tous les utilisateurs, tous rôles confondus
            elif target_type == 'users':
                users = User.objects.filter(role='UTILISATEUR')  # Uniquement les utilisateurs
            elif target_type == 'advertisers':
                users = User.objects.filter(role='ANNONCEUR')  # Uniquement les annonceurs
            elif target_type == 'admin':
                users = User.objects.filter(role='ADMIN')  # Uniquement les administrateurs
            elif target_type == 'staff':
                users = User.objects.filter(is_staff=True)  # Uniquement le staff
            
            created = Notification.send_to_users(users, title, message)
            messages.success(request, f"{len(created)} notifications ont été créées avec succès.")

    def get_fieldsets(self, request, obj=None):
        if not obj:  # Uniquement pour l'ajout
            return (
                ('Campagne de notification', {
                    'fields': ('target_type', 'user', 'title', 'message')
                }),
            )
        return (  # Pour la modification
            ('Informations', {
                'fields': ('user', 'title', 'message', 'is_read')
            }),
            ('Dates', {
                'fields': ('created', 'modified')
            }),
        )

admin.site.register(Preference)

@admin.register(Horaire)
class HoraireAdmin(admin.ModelAdmin):
    list_display = ('annonce', 'jour', 'heure_ouverture', 'heure_fermeture')
    list_filter = ('jour',)

@admin.register(Tarif)
class TarifAdmin(admin.ModelAdmin):
    list_display = ('annonce', 'nom', 'prix')
    search_fields = ('nom',)

@admin.register(GaleriePhoto)
class GaleriePhotoAdmin(admin.ModelAdmin):
    list_display = ('annonce', 'image')
    list_filter = ('annonce',)
