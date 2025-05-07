import requests
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

User = get_user_model()

class GoogleAuthView(APIView):
    def post(self, request):
        token = request.data.get('token')
        
        if not token:
            return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Vérifier le token avec Google
            response = requests.get(
                'https://www.googleapis.com/userinfo/v2/me',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if response.status_code != 200:
                return Response(
                    {'error': 'Invalid token'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            google_data = response.json()
            google_user_id = google_data.get('id')
            email = google_data.get('email')
            
            if not google_user_id or not email:
                return Response(
                    {'error': 'Invalid token, missing user information'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Trouver ou créer l'utilisateur
            user, created = User.objects.get_or_create(
                username=f'google_{google_user_id}',
                defaults={
                    'email': email,
                    'first_name': google_data.get('given_name', ''),
                    'last_name': google_data.get('family_name', '')
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
            
        except Exception as e:
            return Response(
                {'error': f'Authentication failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 