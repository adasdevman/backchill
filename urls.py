from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

def redirect_to_dashboard(request):
    return redirect('dashboard:home')

urlpatterns = [
    path('', redirect_to_dashboard, name='root'),  # Redirection de l'URL racine
    path('admin/', admin.site.urls),
    path('dashboard/', include('core.urls')),
    path('api/', include('api.urls')),  # Ajout du préfixe api/ pour l'API
    path('', include('users.urls')),  # Pour les routes utilisateur
] 

# Servir les fichiers media en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)