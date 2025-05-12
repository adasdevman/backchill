from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from django.db import IntegrityError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserProfileSerializer
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from core.services.email_service import EmailService
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework.authtoken.models import Token
import requests

User = get_user_model()

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

class CustomPasswordResetView(PasswordResetView):
    success_url = reverse_lazy('dashboard:password_reset_done')
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    
    def form_valid(self, form):
        """
        Génère un token de réinitialisation et envoie l'email via notre service d'email personnalisé.
        """
        email = form.cleaned_data["email"]
        for user in form.get_users(email):
            # Génère le token et l'URL de réinitialisation
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = self.request.build_absolute_uri(
                reverse_lazy('dashboard:password_reset_confirm', kwargs={
                    'uidb64': uid,
                    'token': token
                })
            )
            
            # Envoie l'email via notre service
            email_service = EmailService()
            email_service.send_password_reset_email(
                user_email=user.email,
                user_name=user.get_full_name() or user.email,
                reset_url=reset_url
            )
        
        return super().form_valid(form)

@api_view(['POST'])
@permission_classes([AllowAny])
def social_login(request):
    """
    Gère l'authentification via les réseaux sociaux (Google, Apple, Facebook)
    en utilisant les tokens Clerk
    """
    provider = request.data.get('provider')
    token = request.data.get('token')
    
    if not provider or not token:
        return Response(
            {'error': 'Provider and token are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Pour le moment, retournons simplement un token fictif pour tester
        # Vous pourrez implémenter la vérification complète du token plus tard
        user, created = User.objects.get_or_create(
            email=f"{provider}_user@example.com",
            defaults={'username': f"{provider}_user"}
        )
        
        # Créer ou récupérer un token pour cet utilisateur
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username
            }
        })
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def check_email(request):
    """
    Vérifie si un email est disponible pour l'inscription
    """
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email is required'}, status=400)
    
    exists = User.objects.filter(email=email).exists()
    return Response({'exists': exists})
