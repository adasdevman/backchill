import jwt
import json
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

User = get_user_model()

class AppleAuthView(APIView):
    def post(self, request):
        identity_token = request.data.get('identity_token')
        
        if not identity_token:
            return Response({'error': 'Identity token is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Décoder le JWT sans vérifier la signature (pour extraire le payload)
            decoded = jwt.decode(
                identity_token,
                options={"verify_signature": False},
                algorithms=['RS256']
            )
            
            # Récupérer l'email et le sub (user ID) du token
            apple_user_id = decoded.get('sub')
            email = decoded.get('email')
            
            if not apple_user_id or not email:
                return Response(
                    {'error': 'Invalid identity token, missing user information'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Trouver ou créer l'utilisateur
            user, created = User.objects.get_or_create(
                username=f'apple_{apple_user_id}',
                defaults={
                    'email': email,
                    'first_name': request.data.get('first_name', ''),
                    'last_name': request.data.get('last_name', '')
                }
            )
            
            # Générer ou récupérer le token
            token, _ = Token.objects.get_or_create(user=user)
            
            # Informations utilisateur à retourner
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'token': token.key
            }
            
            return Response(user_data, status=status.HTTP_200_OK)
            
        except jwt.InvalidTokenError as e:
            return Response(
                {'error': f'Invalid identity token: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Authentication failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 