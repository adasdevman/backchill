from django.urls import path
from . import views
from .views import CloudinaryUploadView

urlpatterns = [
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/register/annonceur/', views.RegisterView.as_view(), name='register-annonceur'),
    path('auth/check-email/', views.check_email, name='check-email'),
    path('profile/', views.get_profile, name='profile'),
    path('profile/update/', views.update_profile, name='update-profile'),
    path('profile/billing/info/', views.get_billing_info, name='billing-info'),
    path('profile/billing/update/', views.update_billing_info, name='update-billing'),
    path('api/auth/social/', views.social_login, name='social_login'),
    path('api/sync-clerk-user/', views.sync_clerk_user, name='sync_clerk_user'),
    path('api/check-clerk-config/', views.check_clerk_config, name='check_clerk_config'),
    # Route for Cloudinary uploads
    path('cloudinary/upload/', CloudinaryUploadView.as_view(), name='cloudinary_upload'),
]