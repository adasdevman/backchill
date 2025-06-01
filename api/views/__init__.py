# Import all views from the main views.py file
from .. import views

# Re-export all views
from ..views import (
    login_view, register_view, register_annonceur_view,
    profile_view, CategorieList, AnnonceList, AnnonceDetail,
    create_payment, payment_history, CinetPayWebhookView,
    check_email, mes_annonces, mes_tickets, mes_chills,
    NotificationViewSet, upload_annonce_photo, received_bookings,
    sold_tickets, delete_account_view, FacebookDataDeletionView,
    UploadAnnonceVideoView
)

__all__ = [
    'login_view', 'register_view', 'register_annonceur_view',
    'profile_view', 'CategorieList', 'AnnonceList', 'AnnonceDetail',
    'create_payment', 'payment_history', 'CinetPayWebhookView',
    'check_email', 'mes_annonces', 'mes_tickets', 'mes_chills',
    'NotificationViewSet', 'upload_annonce_photo', 'received_bookings',
    'sold_tickets', 'delete_account_view', 'FacebookDataDeletionView',
    'UploadAnnonceVideoView'
]