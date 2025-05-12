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
import os
import json
import logging
import platform

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
                
                # Mettre à jour la source du dernier login
                try:
                    profile = user.profile
                    profile.last_login_source = 'django'
                    profile.save()
                except:
                    # Si le profil n'existe pas, le créer
                    from .models import Profile
                    Profile.objects.create(
                        user=user, 
                        auth_source='django',
                        last_login_source='django'
                    )
                
                # Déterminer la source d'authentification
                auth_source = 'django'
                clerk_user_id = None
                try:
                    profile = user.profile
                    auth_source = profile.auth_source
                    clerk_user_id = profile.clerk_user_id
                except:
                    pass
                
                return Response({
                    'token': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'nom': user.last_name,
                        'prenoms': user.first_name,
                        'auth_source': auth_source,
                        'clerk_user_id': clerk_user_id
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
            
            # Créer ou mettre à jour le profil
            try:
                profile = user.profile
                profile.auth_source = 'django'
                profile.last_login_source = 'django'
                profile.save()
            except:
                from .models import Profile
                Profile.objects.create(
                    user=user,
                    auth_source='django',
                    last_login_source='django'
                )
            
            refresh = RefreshToken.for_user(user)
            return Response({
                'token': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'nom': user.last_name,
                    'prenoms': user.first_name,
                    'auth_source': 'django'
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
    en utilisant les sessions Clerk
    """
    provider = request.data.get('provider')
    session_id = request.data.get('session_id')
    
    if not provider or not session_id:
        return Response(
            {'error': 'Provider and session_id are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Récupérer le jeton JWT à partir du session_id de Clerk
        # Obtenir la clé secrète de Clerk des variables d'environnement
        clerk_secret_key = os.environ.get('CLERK_SECRET_KEY')
        
        if not clerk_secret_key:
            return Response(
                {'error': 'CLERK_SECRET_KEY is not configured on the server'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Faire une requête à l'API Clerk pour échanger le session_id contre un token JWT
        clerk_response = requests.post(
            'https://api.clerk.dev/v1/sessions/' + session_id + '/tokens',
            headers={
                'Authorization': f'Bearer {clerk_secret_key}',
                'Content-Type': 'application/json'
            },
            json={}  # Corps vide de la requête POST
        )
        
        if clerk_response.status_code != 200:
            return Response(
                {'error': f'Failed to exchange session ID for JWT: {clerk_response.text}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        clerk_data = clerk_response.json()
        jwt_token = clerk_data.get('jwt')
        
        if not jwt_token:
            return Response(
                {'error': 'No JWT found in Clerk response'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier le token JWT pour obtenir les informations utilisateur
        session_response = requests.get(
            'https://api.clerk.dev/v1/sessions/' + session_id,
            headers={
                'Authorization': f'Bearer {clerk_secret_key}',
                'Content-Type': 'application/json'
            }
        )
        
        if session_response.status_code != 200:
            return Response(
                {'error': f'Failed to get user info: {session_response.text}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session_data = session_response.json()
        
        # Extraire les informations utilisateur
        user_id = session_data.get('user_id')
        
        # Obtenir les données utilisateur complètes
        user_response = requests.get(
            'https://api.clerk.dev/v1/users/' + user_id,
            headers={
                'Authorization': f'Bearer {clerk_secret_key}',
                'Content-Type': 'application/json'
            }
        )
        
        if user_response.status_code != 200:
            return Response(
                {'error': f'Failed to get user details: {user_response.text}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_data = user_response.json()
        
        # Récupérer l'email principal de l'utilisateur
        primary_email = None
        if user_data.get('email_addresses'):
            for email_obj in user_data.get('email_addresses', []):
                if email_obj.get('id') == user_data.get('primary_email_address_id'):
                    primary_email = email_obj.get('email_address')
                    break
        
        if not primary_email:
            return Response(
                {'error': 'Could not find primary email for user'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Créer ou mettre à jour l'utilisateur dans notre système
        try:
            user = User.objects.get(email=primary_email)
        except User.DoesNotExist:
            # Créer un nouvel utilisateur
            logger.info(f"Création d'un nouvel utilisateur avec email: {primary_email}")
            first_name = user_data.get('first_name', '')
            last_name = user_data.get('last_name', '')
            
            # La méthode create_user attend l'email comme premier argument
            # et génère le username automatiquement
            user = User.objects.create_user(
                email=primary_email,
                first_name=first_name,
                last_name=last_name,
                # Définir un mot de passe aléatoire pour la sécurité
                password=User.objects.make_random_password()
            )
        
        # Utiliser uniquement le refresh token JWT 
        refresh = RefreshToken.for_user(user)
        logger.info(f"Refresh token JWT créé pour {user.email}")
        
        response_data = {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'email': user.email,
                'nom': user.last_name,
                'prenoms': user.first_name,
                'auth_source': 'clerk',
                'clerk_user_id': user_id
            }
        }
        
        logger.info(f"Synchronisation réussie pour {user.email}")
        return Response(response_data)
    
    except Exception as e:
        logger.exception(f"Exception non gérée dans sync_clerk_user: {str(e)}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def check_clerk_config(request):
    """
    Endpoint de diagnostic pour vérifier la configuration Clerk
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Vérifier la clé API
        clerk_secret_key = os.environ.get('CLERK_SECRET_KEY')
        has_secret_key = bool(clerk_secret_key)
        
        # Ne pas exposer la clé complète pour des raisons de sécurité
        masked_key = None
        if clerk_secret_key:
            masked_key = f"sk_****{clerk_secret_key[-4:]}" if len(clerk_secret_key) > 8 else "présente mais trop courte"
        
        # Essayer d'appeler l'API Clerk pour vérifier si la clé fonctionne
        api_works = False
        api_error = None
        
        if clerk_secret_key:
            try:
                # Test simple: liste des utilisateurs (max 1)
                response = requests.get(
                    'https://api.clerk.dev/v1/users?limit=1',
                    headers={
                        'Authorization': f'Bearer {clerk_secret_key}',
                        'Content-Type': 'application/json'
                    }
                )
                
                api_works = response.status_code == 200
                
                if not api_works:
                    # Afficher plus de détails sur l'erreur
                    api_error = f"Code: {response.status_code}, Réponse: {response.text}"
                    logger.error(f"Test de l'API Clerk échoué: {api_error}")
                    
                    # Tester si une méthode POST fonctionnerait mieux (pour le diagnostic)
                    try:
                        test_post = requests.post(
                            'https://api.clerk.dev/v1/users?limit=1',
                            headers={
                                'Authorization': f'Bearer {clerk_secret_key}',
                                'Content-Type': 'application/json'
                            },
                            json={}
                        )
                        if test_post.status_code == 200:
                            api_error += " [POST fonctionne mais pas GET]"
                            logger.info("La méthode POST fonctionne pour l'API")
                    except Exception as post_e:
                        logger.error(f"Test POST a également échoué: {str(post_e)}")
            except Exception as e:
                api_error = str(e)
                logger.exception(f"Exception lors du test de l'API Clerk: {api_error}")
        
        return Response({
            'has_secret_key': has_secret_key,
            'masked_key': masked_key,
            'api_works': api_works,
            'api_error': api_error,
            'python_version': platform.python_version(),
            'environment': os.environ.get('DJANGO_SETTINGS_MODULE', 'inconnu')
        })
    except Exception as e:
        logger.exception(f"Exception dans check_clerk_config: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

@api_view(['POST'])
@permission_classes([AllowAny])
def sync_clerk_user(request):
    """
    Synchronise un utilisateur authentifié via Clerk avec notre système
    Accepte soit un JWT, soit directement un session_id
    """
    jwt_token = request.data.get('jwt')
    session_id = request.data.get('session_id')
    
    logger = logging.getLogger(__name__)
    
    logger.info(f"Début de sync_clerk_user avec session_id: {session_id and session_id[:10]}...")
    
    if not (jwt_token or session_id):
        logger.error("Erreur: ni jwt ni session_id fourni")
        return Response(
            {'error': 'Either jwt or session_id is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Obtenir la clé secrète de Clerk des variables d'environnement
        clerk_secret_key = os.environ.get('CLERK_SECRET_KEY')
        
        if not clerk_secret_key:
            logger.error("Erreur: CLERK_SECRET_KEY manquante dans les variables d'environnement")
            return Response(
                {'error': 'CLERK_SECRET_KEY is not configured on the server'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        logger.info("Clé API Clerk trouvée, longueur: " + str(len(clerk_secret_key)))
        
        # Si nous avons un session_id, obtenons d'abord le JWT
        if session_id and not jwt_token:
            try:
                logger.info(f"Tentative d'échange du session_id contre un JWT: {session_id[:10]}...")
                
                # Log complet de la requête pour debug
                url = f'https://api.clerk.dev/v1/sessions/{session_id}/tokens'
                headers = {
                    'Authorization': f'Bearer {clerk_secret_key}',
                    'Content-Type': 'application/json'
                }
                logger.info(f"URL d'appel: {url}")
                logger.info(f"Headers: Authorization: Bearer sk_****{clerk_secret_key[-4:]}")
                
                clerk_response = requests.post(
                    url,
                    headers=headers,
                    json={}  # Corps vide de la requête POST
                )
                
                logger.info(f"Code de statut de la réponse Clerk: {clerk_response.status_code}")
                
                if clerk_response.status_code != 200:
                    error_msg = f"Échec de l'échange du session_id. Code: {clerk_response.status_code}, Réponse: {clerk_response.text}"
                    logger.error(error_msg)
                    return Response(
                        {'error': error_msg}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                clerk_data = clerk_response.json()
                jwt_token = clerk_data.get('jwt')
                
                if not jwt_token:
                    logger.error(f"Pas de JWT trouvé dans la réponse Clerk: {clerk_data}")
                    return Response(
                        {'error': f'No JWT found in Clerk response: {clerk_data}'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                logger.info("JWT obtenu avec succès")
                
            except Exception as e:
                logger.exception(f"Exception lors de l'échange session_id contre JWT: {str(e)}")
                return Response(
                    {'error': f'Failed to exchange session ID for JWT: {str(e)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Vérifier le JWT pour obtenir l'ID utilisateur
        try:
            logger.info("Décodage du JWT...")
            import jwt as pyjwt
            decoded = pyjwt.decode(jwt_token, options={"verify_signature": False})
            user_id = decoded.get('sub')
            
            if not user_id:
                logger.error(f"Pas d'ID utilisateur trouvé dans le JWT: {decoded}")
                return Response(
                    {'error': 'Invalid JWT token: missing user ID'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            logger.info(f"ID utilisateur extrait du JWT: {user_id}")
            
        except Exception as e:
            logger.exception(f"Exception lors du décodage du JWT: {str(e)}")
            return Response(
                {'error': f'Failed to decode JWT: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtenir les données utilisateur complètes depuis Clerk
        try:
            logger.info(f"Récupération des détails utilisateur depuis Clerk pour user_id: {user_id}")
            
            # Vérifier si on doit utiliser GET ou POST
            user_response = requests.get(
                f'https://api.clerk.dev/v1/users/{user_id}',
                headers={
                    'Authorization': f'Bearer {clerk_secret_key}',
                    'Content-Type': 'application/json'
                }
            )
            
            logger.info(f"Code de statut de la réponse des détails utilisateur: {user_response.status_code}")
            
            if user_response.status_code != 200:
                error_msg = f"Échec de la récupération des détails utilisateur. Code: {user_response.status_code}, Réponse: {user_response.text}"
                logger.error(error_msg)
                return Response(
                    {'error': error_msg}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user_data = user_response.json()
            logger.info(f"Données utilisateur récupérées: {user_data.get('id')} - {user_data.get('email_addresses')}")
            
        except Exception as e:
            logger.exception(f"Exception lors de la récupération des détails utilisateur: {str(e)}")
            return Response(
                {'error': f'Failed to get user details: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Récupérer l'email principal de l'utilisateur
        primary_email = None
        email_verified = False
        
        if user_data.get('email_addresses'):
            for email_obj in user_data.get('email_addresses', []):
                if email_obj.get('id') == user_data.get('primary_email_address_id'):
                    primary_email = email_obj.get('email_address')
                    email_verified = email_obj.get('verification', {}).get('status') == 'verified'
                    break
        
        if not primary_email:
            logger.error(f"Pas d'email principal trouvé pour l'utilisateur: {user_data}")
            return Response(
                {'error': 'Could not find primary email for user'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logger.info(f"Email principal trouvé: {primary_email} (vérifié: {email_verified})")
        
        # Créer ou mettre à jour l'utilisateur dans notre système
        try:
            user = User.objects.get(email=primary_email)
            logger.info(f"Utilisateur existant trouvé avec email: {primary_email}")
            
            # Mettre à jour les informations utilisateur si nécessaire
            update_needed = False
            if user.first_name != user_data.get('first_name', '') and user_data.get('first_name'):
                user.first_name = user_data.get('first_name', '')
                update_needed = True
            
            if user.last_name != user_data.get('last_name', '') and user_data.get('last_name'):
                user.last_name = user_data.get('last_name', '')
                update_needed = True
            
            # Si l'utilisateur existe déjà mais a été créé par un processus Django, 
            # mettre à jour le champ auth_source
            try:
                profile = user.profile
                logger.info(f"Profil existant trouvé: source={profile.auth_source}")
                if profile.auth_source != 'clerk':
                    profile.auth_source = 'clerk'
                    profile.clerk_user_id = user_id
                    profile.save()
                    logger.info(f"Profil mis à jour pour l'utilisateur {user.email}: auth_source=clerk, clerk_user_id={user_id}")
            except Exception as profile_error:
                logger.exception(f"Exception lors de l'accès au profil: {str(profile_error)}")
                # Si le profil n'existe pas encore, le créer
                from .models import Profile
                # Utiliser get_or_create pour éviter les doublons
                profile, created = Profile.objects.get_or_create(
                    user=user,
                    defaults={
                        'auth_source': 'clerk',
                        'clerk_user_id': user_id,
                        'email_verified': email_verified
                    }
                )
                if not created:
                    # Si le profil existait déjà, mettre à jour les champs
                    profile.auth_source = 'clerk'
                    profile.clerk_user_id = user_id
                    profile.email_verified = email_verified
                    profile.save()
                
                logger.info(f"Profil {'créé' if created else 'mis à jour'} pour l'utilisateur {user.email}")
                
            if update_needed:
                user.save()
                logger.info(f"Informations utilisateur mises à jour pour {user.email}")
                
        except User.DoesNotExist:
            # Créer un nouvel utilisateur
            logger.info(f"Création d'un nouvel utilisateur avec email: {primary_email}")
            first_name = user_data.get('first_name', '')
            last_name = user_data.get('last_name', '')
            
            # La méthode create_user attend l'email comme premier argument
            # et génère le username automatiquement
            user = User.objects.create_user(
                email=primary_email,
                first_name=first_name,
                last_name=last_name,
                # Définir un mot de passe aléatoire pour la sécurité
                password=User.objects.make_random_password()
            )
            logger.info(f"Nouvel utilisateur créé: {user.email}")
            
            # Créer un profil pour l'utilisateur
            from .models import Profile
            # Utiliser get_or_create pour éviter les doublons
            profile, created = Profile.objects.get_or_create(
                user=user,
                defaults={
                    'auth_source': 'clerk',
                    'clerk_user_id': user_id,
                    'email_verified': email_verified
                }
            )
            if not created:
                # Si le profil existait déjà, mettre à jour les champs
                profile.auth_source = 'clerk'
                profile.clerk_user_id = user_id
                profile.email_verified = email_verified
                profile.save()
            
            logger.info(f"Profil {'créé' if created else 'mis à jour'} pour le nouvel utilisateur {user.email}")
        
        # Utiliser uniquement le refresh token JWT au lieu du token legacy
        refresh = RefreshToken.for_user(user)
        logger.info(f"Refresh token JWT créé pour {user.email}")
        
        response_data = {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'email': user.email,
                'nom': user.last_name,
                'prenoms': user.first_name,
                'auth_source': 'clerk',
                'clerk_user_id': user_id
            }
        }
        
        logger.info(f"Synchronisation réussie pour {user.email}")
        return Response(response_data)
    
    except Exception as e:
        logger.exception(f"Exception non gérée dans sync_clerk_user: {str(e)}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
