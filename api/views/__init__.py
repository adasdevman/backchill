# Exporter les vues spécifiques à Cloudinary depuis leurs modules respectifs
from .cloudinary_views import CloudinaryUploadView
from .cloudinary_admin_views import CloudinarySetupView
from .cloudinary_config_view import CloudinaryConfigView

# Pour toutes les autres vues, nous allons simplement définir les noms sans les importer
# Ces noms seront résolus lors de l'importation depuis urls.py directement vers views.py
__all__ = [
    'CloudinaryUploadView',
    'CloudinarySetupView',
    'CloudinaryConfigView'
]