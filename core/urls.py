from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from users.views import CustomPasswordResetView
from django.urls import reverse_lazy

app_name = 'dashboard'  # Important pour les redirections avec namespace

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('login/', views.dashboard_login, name='login'),
    path('logout/', views.dashboard_logout, name='logout'),
    path('users/', views.user_list, name='users'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:user_id>/detail/', views.user_detail, name='user_detail'),
    path('annonces/', views.annonce_list, name='annonces'),
    path('annonces/create/', views.annonce_create, name='annonce_create'),
    path('annonces/<int:annonce_id>/edit/', views.annonce_edit, name='annonce_edit'),
    path('annonces/<int:annonce_id>/delete/', views.annonce_delete, name='annonce_delete'),
    path('annonces/<int:annonce_id>/detail/', views.annonce_detail, name='annonce_detail'),
    path('annonces/<int:annonce_id>/duplicate/', views.annonce_duplicate, name='annonce_duplicate'),
    path('statistiques/', views.statistiques, name='statistiques'),
    
    # URLs des paiements
    path('payments/', views.payment_list, name='payments'),
    path('payments/<int:payment_id>/', views.payment_detail, name='payment_detail'),
    path('payments/<int:payment_id>/edit/', views.payment_edit, name='payment_edit'),
    path('payments/<int:payment_id>/delete/', views.payment_delete, name='payment_delete'),
    
    # URLs publiques pour les catégories et annonces
    path('api/categories/', views.categories, name='categories'),
    path('api/annonces/filtrer/', views.annonces_par_categorie, name='annonces_par_categorie'),
    path('api/annonces/publiques/', views.annonces_publiques, name='annonces_publiques'),

    # URLs de réinitialisation de mot de passe avec les success_url corrects
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url=reverse_lazy('dashboard:password_reset_complete')
    ), name='password_reset_confirm'),
    
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
] 