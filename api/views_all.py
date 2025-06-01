# Copy of the original views.py file
# This file is created as a backup to ensure all views are available

from api.views import (
    login_view, register_view, register_annonceur_view,
    profile_view, CategorieList, AnnonceList, AnnonceDetail,
    create_payment, payment_history, CinetPayWebhookView,
    check_email, mes_annonces, mes_tickets, mes_chills,
    NotificationViewSet, upload_annonce_photo, received_bookings,
    sold_tickets, delete_account_view, FacebookDataDeletionView,
    UploadAnnonceVideoView
)

# Export all the views
__all__ = [
    'login_view', 'register_view', 'register_annonceur_view',
    'profile_view', 'CategorieList', 'AnnonceList', 'AnnonceDetail',
    'create_payment', 'payment_history', 'CinetPayWebhookView',
    'check_email', 'mes_annonces', 'mes_tickets', 'mes_chills',
    'NotificationViewSet', 'upload_annonce_photo', 'received_bookings',
    'sold_tickets', 'delete_account_view', 'FacebookDataDeletionView',
    'UploadAnnonceVideoView'
]
