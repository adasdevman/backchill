from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Utiliser le module d'importation robuste qui gère les erreurs potentielles
from .views_imports import (
    login_view, register_view, register_annonceur_view,
    profile_view, CategorieList, AnnonceList, AnnonceDetail,
    create_payment, payment_history, CinetPayWebhookView,
    check_email, mes_annonces, mes_tickets, mes_chills,
    NotificationViewSet, upload_annonce_photo, received_bookings,
    sold_tickets, delete_account_view, FacebookDataDeletionView,
    UploadAnnonceVideoView
)

# Import explicites des vues Cloudinary depuis leurs modules spécifiques
from api.views.cloudinary_views import CloudinaryUploadView
from api.views.cloudinary_admin_views import CloudinarySetupView
from api.views.cloudinary_config_view import CloudinaryConfigView
from rest_framework_simplejwt.views import TokenRefreshView
from .auth.apple import AppleAuthView
from .auth.google import GoogleAuthView

app_name = 'api'

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register('notifications', NotificationViewSet, basename='notification')

# First create the base URL patterns
urlpatterns = [
    path('auth/login/', login_view, name='login'),
    path('auth/register/', register_view, name='register'),
    path('auth/register/annonceur/', register_annonceur_view, name='register-annonceur'),
    path('auth/delete-account/', delete_account_view, name='delete-account'),
    path('profile/', profile_view, name='profile'),
    path('categories/', CategorieList.as_view(), name='category-list'),
    path('annonces/', AnnonceList.as_view(), name='annonce-list'),
    path('annonces/<int:pk>/', AnnonceDetail.as_view(), name='annonce-detail'),
    path('annonces/<int:pk>/photos/', upload_annonce_photo, name='upload-annonce-photo'),
    path('annonces/<int:pk>/video/', UploadAnnonceVideoView.as_view(), name='upload-annonce-video'),
    path('payments/create/', create_payment, name='create-payment'),
    path('payments/history/', payment_history, name='payment-history'),
    path('payments/received-bookings/', received_bookings, name='received-bookings'),
    path('payments/sold-tickets/', sold_tickets, name='sold-tickets'),
    path('payments/webhook/cinetpay/', CinetPayWebhookView.as_view(), name='cinetpay-webhook'),
    path('auth/check-email/', check_email, name='check-email'),
    path('annonces/mes-annonces/', mes_annonces, name='mes-annonces'),
    path('annonces/mes-tickets/', mes_tickets, name='mes-tickets'),
    path('annonces/mes-chills/', mes_chills, name='mes-chills'),
    path('facebook/data-deletion/', FacebookDataDeletionView.as_view(), name='facebook-data-deletion'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/apple', AppleAuthView.as_view(), name='apple_auth'),
    path('auth/google', GoogleAuthView.as_view(), name='google_auth'),
    path('cloudinary/upload/', CloudinaryUploadView.as_view(), name='cloudinary-upload'),
    path('cloudinary/setup/', CloudinarySetupView.as_view(), name='cloudinary-setup'),
    path('cloudinary/config/', CloudinaryConfigView.as_view(), name='cloudinary-config'),
]

# Then extend the urlpatterns with the router URLs
urlpatterns.extend(router.urls)