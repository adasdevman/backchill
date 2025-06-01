import cloudinary
import cloudinary.api
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Configure un upload preset dans Cloudinary pour permettre les téléchargements directs depuis le frontend'
    
    def handle(self, *args, **options):
        try:
            # S'assurer que Cloudinary est correctement configuré
            cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME')
            api_key = settings.CLOUDINARY_STORAGE.get('API_KEY')
            api_secret = settings.CLOUDINARY_STORAGE.get('API_SECRET')
            
            if not all([cloud_name, api_key, api_secret]):
                self.stderr.write(self.style.ERROR(
                    'Configuration Cloudinary incomplète. Vérifiez les paramètres CLOUDINARY_STORAGE.'
                ))
                return
                
            # Configurer Cloudinary
            cloudinary.config(
                cloud_name=cloud_name,
                api_key=api_key,
                api_secret=api_secret
            )
            
            # Créer ou mettre à jour le preset pour les téléchargements non signés
            preset_name = "chillnow_mobile_upload"
            
            # Vérifier si le preset existe déjà
            try:
                existing_preset = cloudinary.api.upload_preset(preset_name)
                self.stdout.write(f"Upload preset '{preset_name}' existe déjà, mise à jour...")
            except Exception:
                self.stdout.write(f"Upload preset '{preset_name}' n'existe pas, création...")
            
            # Créer ou mettre à jour le preset
            preset = cloudinary.api.create_upload_preset(
                name=preset_name,
                unsigned=True,
                folder="mobile_uploads",
                allowed_formats="mp4,webm,mov,avi,mkv",
                resource_type="video",
            )
            
            self.stdout.write(self.style.SUCCESS(
                f"Upload preset '{preset_name}' créé avec succès. "
                f"Configuration pour le frontend: "
                f"CLOUDINARY_UPLOAD_PRESET='{preset_name}', "
                f"CLOUDINARY_CLOUD_NAME='{cloud_name}'"
            ))
            
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Erreur: {str(e)}"))
