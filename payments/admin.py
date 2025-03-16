from django.contrib import admin
from .models import Payment # type: ignore

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'get_annonce_title', 'amount', 'status', 'payment_type', 'created_at')
    list_filter = ('status', 'payment_type', 'created_at')
    search_fields = ('transaction_id', 'user__email', 'annonce__titre')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('user', 'annonce', 'amount', 'status', 'payment_type')
        }),
        ('Transaction', {
            'fields': ('transaction_id', 'description')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def get_annonce_title(self, obj):
        return obj.annonce.titre if obj.annonce else "N/A"
    get_annonce_title.short_description = "Annonce"
