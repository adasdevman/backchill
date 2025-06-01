"""
Initialise le module views
Ce fichier est volontairement minimaliste pour éviter les problèmes d'importation circulaire
"""

# Importer seulement les modules Cloudinary qui sont dans ce répertoire
from .cloudinary_views import CloudinaryUploadView
from .cloudinary_admin_views import CloudinarySetupView
from .cloudinary_config_view import CloudinaryConfigView

__all__ = [
    'CloudinaryUploadView',
    'CloudinarySetupView',
    'CloudinaryConfigView'
]