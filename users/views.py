from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from django.db import IntegrityError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import UserProfileSerializer

class LoginView(APIView):
    permission_classes = []  # Permettre l'accès sans authentification
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        try:
            # On récupère d'abord l'utilisateur par email
            user = User.objects.get(email=email)
            # Puis on authentifie avec le username
            auth_user = authenticate(username=user.username, password=password)
            
            if auth_user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'token': str(refresh.access_token),
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'nom': user.last_name,
                        'prenoms': user.first_name
                    }
                })
            return Response(
                {'error': 'Mot de passe incorrect'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'Email non trouvé'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class RegisterView(APIView):
    permission_classes = []  # Permettre l'accès sans authentification
    
    def post(self, request):
        try:
            nom = request.data.get('nom')
            prenoms = request.data.get('prenoms')
            email = request.data.get('email')
            password = request.data.get('password')
            
            # On utilise l'email comme username
            user = User.objects.create_user(
                username=email,  # Important : username = email
                email=email,
                password=password,
                first_name=prenoms,
                last_name=nom
            )
            
            refresh = RefreshToken.for_user(user)
            return Response({
                'token': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'nom': user.last_name,
                    'prenoms': user.first_name
                }
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    serializer = UserProfileSerializer(
        request.user,
        data=request.data,
        partial=True
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_billing_info(request):
    return Response({
        'address': request.user.address or '',
        'city': request.user.city or '',
    })

@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def update_billing_info(request):
    try:
        user = request.user
        user.address = request.data.get('address', user.address)
        user.city = request.data.get('city', user.city)
        user.save()
        return Response({
            'address': user.address,
            'city': user.city,
        })
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )
