import cloudinary
import cloudinary.api
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class CloudinarySetupView(APIView):
    """
    Vue pour configurer Cloudinary (preset, etc.) pour les téléchargements directs.
    Réservée aux administrateurs.
    """
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        try:
            # S'assurer que Cloudinary est correctement configuré
            cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME')
            api_key = settings.CLOUDINARY_STORAGE.get('API_KEY')
            api_secret = settings.CLOUDINARY_STORAGE.get('API_SECRET')
            
            if not all([cloud_name, api_key, api_secret]):
                return Response({
                    'error': 'Configuration Cloudinary incomplète. Vérifiez les paramètres CLOUDINARY_STORAGE.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
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
                logger.info(f"Upload preset '{preset_name}' existe déjà, mise à jour...")
            except Exception:
                logger.info(f"Upload preset '{preset_name}' n'existe pas, création...")
            
            # Créer ou mettre à jour le preset
            preset = cloudinary.api.create_upload_preset(
                name=preset_name,
                unsigned=True,
                folder="mobile_uploads",
                allowed_formats="mp4,webm,mov,avi,mkv",
                resource_type="video",
            )
            
            return Response({
                'success': True,
                'message': f"Upload preset '{preset_name}' créé avec succès.",
                'preset': preset_name,
                'cloud_name': cloud_name
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de la configuration Cloudinary: {str(e)}", exc_info=True)
            return Response({
                'error': f'La configuration de Cloudinary a échoué: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
