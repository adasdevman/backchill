import cloudinary
import cloudinary.uploader
import cloudinary.api
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import logging

logger = logging.getLogger(__name__)

class CloudinaryUploadView(APIView):
    """
    Vue pour télécharger des fichiers (images/vidéos) vers Cloudinary.
    Cela permet aux applications clientes (notamment l'application mobile) de télécharger 
    des fichiers via le backend Django au lieu d'interagir directement avec Cloudinary.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            logger.info(f"Tentative de téléchargement Cloudinary reçue")
            
            if 'file' not in request.FILES:
                logger.warning("Aucun fichier n'a été fourni")
                return Response({
                    'error': 'Aucun fichier à télécharger n\'a été fourni'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            file_to_upload = request.FILES['file']
            resource_type = request.POST.get('resource_type', 'auto')  # 'image', 'video', 'raw', ou 'auto'
            transformations = request.POST.get('transformations', '')  # Options de transformation
            
            logger.info(f"Téléchargement de {file_to_upload.name} ({resource_type}) vers Cloudinary")
              # Configurer les options de téléchargement
            upload_options = {
                'resource_type': resource_type,
                'folder': 'mobile_uploads',
                'use_filename': True,
                'unique_filename': True
            }
            
            # Utiliser le preset ml_default si indiqué
            preset = request.POST.get('upload_preset', '')
            if preset:
                upload_options['upload_preset'] = preset
                logger.info(f"Utilisation du preset: {preset}")
            
            # Appliquer des transformations si spécifiées
            if transformations:
                upload_options['transformation'] = transformations
                
            # Télécharger le fichier vers Cloudinary
            upload_result = cloudinary.uploader.upload(file_to_upload, **upload_options)
            
            logger.info(f"Téléchargement Cloudinary réussi: {upload_result.get('public_id')}")
            
            # Renvoyer l'URL et d'autres informations pertinentes
            return Response({
                'success': True,
                'url': upload_result.get('secure_url'),
                'public_id': upload_result.get('public_id'),
                'resource_type': upload_result.get('resource_type')
            })
            
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement vers Cloudinary: {str(e)}", exc_info=True)
            return Response({
                'error': f'Le téléchargement vers Cloudinary a échoué: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
