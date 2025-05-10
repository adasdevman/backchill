from django.urls import path
from . import views

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
] 