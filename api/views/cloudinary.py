import cloudinary
import cloudinary.uploader
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
import logging

logger = logging.getLogger(__name__)

class CloudinaryUploadView(APIView):
    """
    API endpoint pour télécharger directement un fichier vers Cloudinary
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        logger.info("Demande de téléchargement vers Cloudinary reçue")
        
        if 'file' not in request.FILES:
            logger.error("Aucun fichier fourni dans la demande")
            return Response(
                {'error': 'Aucun fichier fourni'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file_obj = request.FILES['file']
        resource_type = request.POST.get('resource_type', 'auto')
        transformations = request.POST.get('transformations', None)
        
        logger.info(f"Type de fichier: {file_obj.content_type}, taille: {file_obj.size}, type de ressource: {resource_type}")
        
        try:
            upload_options = {
                'resource_type': resource_type,
            }
            
            # Ajouter des transformations si spécifiées
            if transformations:
                upload_options['transformation'] = transformations

            # Télécharger le fichier vers Cloudinary
            upload_result = cloudinary.uploader.upload(file_obj, **upload_options)
            
            logger.info(f"Téléchargement Cloudinary réussi: {upload_result.get('public_id')}")
            
            response_data = {
                'public_id': upload_result.get('public_id'),
                'url': upload_result.get('url'),
                'secure_url': upload_result.get('secure_url'),
                'format': upload_result.get('format'),
                'resource_type': upload_result.get('resource_type')
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement vers Cloudinary: {str(e)}", exc_info=True)
            return Response(
                {'error': f"Erreur lors du téléchargement: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
