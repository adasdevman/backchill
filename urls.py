from django.contrib import admin
from django.urls import path, include
from users.views import CloudinaryUploadView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('core.urls')),
    path('api/', include('users.urls')),
    # Routes pour Cloudinary
    path('api/cloudinary/upload/', CloudinaryUploadView.as_view(), name='cloudinary_upload'),
] 