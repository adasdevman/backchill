from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from users.models import User
from core.models import (
    Categorie, SousCategorie, Annonce,
    GaleriePhoto, Horaire, Payment, Tarif, Notification
)
from core.serializers import (
    AnnonceListSerializer,
    AnnonceSerializer,
    AnnonceDetailSerializer,
    CategorieSerializer,
    SousCategorieSerializer,
    HoraireSerializer,
    TarifSerializer,
    GaleriePhotoSerializer,
    PaymentSerializer,
    NotificationSerializer
)
from .serializers.auth import (
    UserSerializer,
    LoginSerializer,
    RegisterSerializer,
    UpdateProfileSerializer,
    AnnonceurRegisterSerializer
)
from users.serializers import UserProfileSerializer
from django.core.exceptions import ValidationError
import logging
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.decorators import action
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from core.services.email_service import EmailService

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    try:
        logger.info(f"Login attempt received for email: {request.data.get('email', 'not provided')}")
        
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Login validation failed: {serializer.errors}")
            return Response(
                {'error': 'Validation failed', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        logger.info(f"Checking if user exists with email: {email}")
        
        # Check if user exists and authenticate
        user = authenticate(request, email=email, password=password)
        if user is None:
            logger.warning(f"Authentication failed for email: {email}")
            return Response(
                {'error': 'Email ou mot de passe incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.is_active:
            logger.warning(f"Inactive user attempted to login: {email}")
            return Response(
                {'error': 'Ce compte est inactif'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'profile_image': user.profile_image.url if user.profile_image else None
            }
        })
        
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Une erreur inattendue est survenue'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        # Envoyer l'email de bienvenue avec le rôle UTILISATEUR
        email_service = EmailService()
        email_service.send_welcome_email(
            user_email=user.email,
            first_name=user.first_name or 'Utilisateur',
            role='UTILISATEUR'
        )
        
        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_annonceur_view(request):
    serializer = AnnonceurRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        # Envoyer l'email de bienvenue avec le rôle ANNONCEUR
        email_service = EmailService()
        email_service.send_welcome_email(
            user_email=user.email,
            first_name=user.first_name or 'Annonceur',
            role='ANNONCEUR'
        )
        
        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    if request.method == 'GET':
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategorieList(generics.ListAPIView):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class AnnonceList(generics.ListCreateAPIView):
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AnnonceSerializer
        return AnnonceListSerializer

    def get_queryset(self):
        queryset = Annonce.objects.filter(est_actif=True)
        
        # Récupérer les paramètres de filtrage
        category_id = self.request.query_params.get('categorie')
        subcategory_id = self.request.query_params.get('sous_categorie')
        status = self.request.query_params.get('status')
        search_query = self.request.query_params.get('search')

        # Filtrer par catégorie
        if category_id:
            queryset = queryset.filter(categorie_id=category_id)
        
        # Filtrer par sous-catégorie
        if subcategory_id:
            queryset = queryset.filter(sous_categorie_id=subcategory_id)

        # Filtrer par statut
        if status:
            queryset = queryset.filter(status=status)

        # Recherche textuelle
        if search_query:
            queryset = queryset.filter(
                Q(titre__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(localisation__icontains=search_query)
            )

        return queryset.select_related(
            'categorie', 
            'sous_categorie'
        ).prefetch_related(
            'photos',
            'horaire_set'
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        print("🔍 Données reçues:", request.data)  # Log des données reçues
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            print("✅ Données validées:", serializer.validated_data)  # Log des données validées
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print("❌ Erreurs de validation:", serializer.errors)  # Log des erreurs
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)

class AnnonceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Annonce.objects.all()
    serializer_class = AnnonceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Annonce.objects.select_related(
            'categorie',
            'sous_categorie'
        ).prefetch_related(
            'photos',
            'horaire_set'
        )

    def perform_update(self, serializer):
        serializer.save(utilisateur=self.request.user)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment(request):
    """Crée un nouveau paiement."""
    try:
        # Accepter les deux formats de paramètres
        annonce_id = request.data.get('annonce_id') or request.data.get('annonce')
        tarif_id = request.data.get('tarif_id') or request.data.get('tarif')
        payment_type = request.data.get('payment_type')

        logger.info(f"Creating payment with: annonce_id={annonce_id}, tarif_id={tarif_id}, payment_type={payment_type}")

        if not all([annonce_id, tarif_id, payment_type]):
            return Response(
                {'error': 'Paramètres manquants'},
                status=400
            )

        # Récupérer l'annonce et le tarif
        try:
            annonce = Annonce.objects.get(id=annonce_id)
            tarif = Tarif.objects.get(id=tarif_id)
        except (Annonce.DoesNotExist, Tarif.DoesNotExist) as e:
            logger.error(f"Annonce ou tarif non trouvé: {str(e)}")
            return Response(
                {'error': 'Annonce ou tarif non trouvé'},
                status=404
            )

        # Calculer le montant d'avance en fonction du type d'annonce
        montant_total = float(tarif.prix)
        is_event = annonce.categorie.nom == 'EVENT'
        taux_avance = 100 if is_event else annonce.utilisateur.taux_avance
        montant_avance = montant_total if taux_avance == 100 else (montant_total * taux_avance / 100)

        logger.info(f"Payment calculation: total={montant_total}, taux={taux_avance}, avance={montant_avance}, is_event={is_event}")

        # Créer le paiement
        payment = Payment.objects.create(
            user=request.user,
            annonce=annonce,
            tarif=tarif,
            amount=montant_avance,
            payment_type=payment_type,
            status='PENDING'
        )

        # Adapter la réponse en fonction du type d'annonce
        response_data = {
            'id': payment.id,
            'montant_total': montant_total,
        }

        # N'inclure le taux d'avance et le montant d'avance que pour les non-événements
        if not is_event:
            response_data.update({
                'montant_avance': montant_avance,
                'taux_avance': taux_avance
            })

        return Response(response_data)
    except Exception as e:
        logger.error(f"Erreur dans create_payment: {str(e)}", exc_info=True)
        return Response(
            {'error': str(e)},
            status=500
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_history(request):
    payments = Payment.objects.filter(user=request.user)
    serializer = PaymentSerializer(payments, many=True)
    return Response(serializer.data)

class CategorieViewSet(ReadOnlyModelViewSet):
    permission_classes = []
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer

class AnnonceViewSet(ReadOnlyModelViewSet):
    permission_classes = []
    serializer_class = AnnonceSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        queryset = Annonce.objects.filter(est_actif=True)
        category_id = self.request.query_params.get('categorie', None)
        subcategory_id = self.request.query_params.get('sous_categorie', None)
        status = self.request.query_params.get('status', 'ACTIVE')  # Par défaut, on ne montre que les annonces actives

        if category_id:
            queryset = queryset.filter(categorie_id=category_id)
        if subcategory_id:
            queryset = queryset.filter(sous_categorie_id=subcategory_id)
        
        # Toujours filtrer par statut
        queryset = queryset.filter(status=status)

        return queryset.select_related('categorie', 'sous_categorie').prefetch_related('photos')

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        query = request.query_params.get('query', '')
        if not query:
            return Response([])

        queryset = self.get_queryset().filter(
            Q(titre__icontains=query) |
            Q(description__icontains=query)
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

@method_decorator(csrf_exempt, name='dispatch')
class CinetPayWebhookView(APIView):
    permission_classes = []
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        try:
            logger.info(f"CinetPay webhook received: {request.data}")

            transaction_id = request.data.get('cpm_trans_id')
            status = request.data.get('status')
            amount = request.data.get('amount')
            currency = request.data.get('currency')
            payment_method = request.data.get('payment_method')
            
            try:
                payment = Payment.objects.get(transaction_id=transaction_id)
            except Payment.DoesNotExist:
                logger.error(f"Payment not found for transaction_id: {transaction_id}")
                return Response({"message": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

            if status == "ACCEPTED":
                payment.status = "completed"
                payment.transaction_data = {
                    "amount": amount,
                    "currency": currency,
                    "payment_method": payment_method,
                    "transaction_id": transaction_id
                }
                payment.save()
                logger.info(f"Payment {transaction_id} marked as completed")
            elif status == "REFUSED":
                payment.status = "failed"
                payment.save()
                logger.info(f"Payment {transaction_id} marked as failed")

            return Response({"message": "Notification processed"}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error processing CinetPay webhook: {str(e)}")
            return Response(
                {"error": "Internal server error"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['POST'])
@permission_classes([AllowAny])
def check_email(request):
    email = request.data.get('email')
    exists = User.objects.filter(email=email).exists()
    return Response({'exists': exists})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mes_annonces(request):
    annonces = Annonce.objects.filter(utilisateur=request.user)
    serializer = AnnonceListSerializer(annonces, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mes_tickets(request):
    tickets = Payment.objects.filter(
        user=request.user,
        payment_type='ticket'
    )
    serializer = PaymentSerializer(tickets, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mes_chills(request):
    """Récupère l'historique des réservations complétées de l'utilisateur."""
    try:
        # Récupérer directement les paiements complétés
        chills = Payment.objects.filter(
            user=request.user,
            status='COMPLETED',
            payment_type='reservation'  # Assurez-vous que c'est le bon type pour les réservations
        )
        
        serializer = PaymentSerializer(chills, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Erreur dans mes_chills: {str(e)}")
        return Response(
            {'error': 'Une erreur est survenue lors de la récupération de vos réservations'},
            status=500
        )

class NotificationViewSet(ModelViewSet):
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['GET'])
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'count': count})
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['POST'])
    def send_to_role(self, request):
        """Envoyer une notification à tous les utilisateurs d'un rôle spécifique"""
        if not request.user.is_staff:
            return Response(
                {"error": "Permission refusée"},
                status=status.HTTP_403_FORBIDDEN
            )

        role = request.data.get('role')
        title = request.data.get('title')
        message = request.data.get('message')

        if not all([role, title, message]):
            return Response(
                {"error": "role, title et message sont requis"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            notifications = Notification.send_to_role(role, title, message)
            return Response({
                "message": f"{len(notifications)} notifications envoyées",
                "role": role
            })
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['POST'])
    def send_to_all(self, request):
        """Envoyer une notification à tous les utilisateurs"""
        if not request.user.is_staff:
            return Response(
                {"error": "Permission refusée"},
                status=status.HTTP_403_FORBIDDEN
            )

        title = request.data.get('title')
        message = request.data.get('message')

        if not all([title, message]):
            return Response(
                {"error": "title et message sont requis"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            notifications = Notification.send_to_all(title, message)
            return Response({
                "message": f"{len(notifications)} notifications envoyées"
            })
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['PATCH'])
    def mark_as_read(self, request, pk=None):
        """Marquer une notification comme lue"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"status": "success"})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_annonce(request):
    print("🔍 Données reçues:", json.dumps(request.data, indent=2))
    
    serializer = AnnonceSerializer(data=request.data)
    if serializer.is_valid():
        print("✅ Données validées:", json.dumps(serializer.validated_data, indent=2))
        try:
            annonce = serializer.save(utilisateur=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print("❌ Erreur lors de la sauvegarde:", str(e))
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        print("❌ Erreurs de validation:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_annonce_photo(request, pk):
    """Upload a photo for an announcement."""
    try:
        annonce = Annonce.objects.get(id=pk)
        
        # Vérifier que l'utilisateur est le propriétaire de l'annonce
        if annonce.utilisateur != request.user:
            return Response(
                {'error': 'Vous n\'êtes pas autorisé à modifier cette annonce'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Vérifier qu'une image a été envoyée
        if 'image' not in request.FILES:
            return Response(
                {'error': 'Aucune image n\'a été envoyée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Créer la photo
        photo = GaleriePhoto.objects.create(
            annonce=annonce,
            image=request.FILES['image']
        )
        
        serializer = GaleriePhotoSerializer(photo)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Annonce.DoesNotExist:
        return Response(
            {'error': 'Annonce non trouvée'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Erreur lors du téléchargement de la photo: {str(e)}")
        return Response(
            {'error': 'Une erreur est survenue lors du téléchargement de la photo'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def received_bookings(request):
    """Récupère les réservations reçues pour les établissements de l'annonceur."""
    try:
        # Récupérer les IDs des annonces de l'annonceur
        annonce_ids = Annonce.objects.filter(utilisateur=request.user).values_list('id', flat=True)
        logger.info(f"IDs des annonces trouvées pour l'utilisateur {request.user.id}: {list(annonce_ids)}")
        
        # Récupérer tous les paiements pour ces annonces pour le débogage
        all_payments = Payment.objects.filter(annonce_id__in=annonce_ids)
        logger.info(f"Nombre total de paiements trouvés: {all_payments.count()}")
        logger.info(f"Types de paiements trouvés: {list(all_payments.values_list('payment_type', flat=True).distinct())}")
        logger.info(f"Statuts trouvés: {list(all_payments.values_list('status', flat=True).distinct())}")
        
        # Récupérer les paiements filtrés
        bookings = Payment.objects.filter(
            annonce_id__in=annonce_ids,
            payment_type__in=['table', 'reservation'],  # Accepter les deux types possibles
            status__in=['completed', 'COMPLETED']  # Accepter les deux formats possibles
        ).order_by('-created')
        
        logger.info(f"Nombre de réservations après filtrage: {bookings.count()}")
        
        serializer = PaymentSerializer(bookings, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Erreur dans received_bookings: {str(e)}")
        return Response(
            {'error': 'Une erreur est survenue lors de la récupération des réservations'},
            status=500
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sold_tickets(request):
    """Récupère les tickets vendus pour les événements de l'annonceur."""
    try:
        # Récupérer les IDs des annonces de l'annonceur
        annonce_ids = Annonce.objects.filter(utilisateur=request.user).values_list('id', flat=True)
        logger.info(f"IDs des événements trouvés pour l'utilisateur {request.user.id}: {list(annonce_ids)}")
        
        # Récupérer tous les paiements de tickets pour ces annonces pour le débogage
        all_tickets = Payment.objects.filter(
            annonce_id__in=annonce_ids,
            payment_type='ticket'
        )
        logger.info(f"Nombre total de tickets trouvés: {all_tickets.count()}")
        logger.info(f"Statuts des tickets trouvés: {list(all_tickets.values_list('status', flat=True).distinct())}")
        
        # Récupérer les tickets vendus (complétés)
        tickets = Payment.objects.filter(
            annonce_id__in=annonce_ids,
            payment_type='ticket',
            status__in=['completed', 'COMPLETED']  # Accepter les deux formats possibles
        ).order_by('-created')
        
        logger.info(f"Nombre de tickets vendus après filtrage: {tickets.count()}")
        
        serializer = PaymentSerializer(tickets, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Erreur dans sold_tickets: {str(e)}")
        return Response(
            {'error': 'Une erreur est survenue lors de la récupération des tickets vendus'},
            status=500
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_account_view(request):
    """
    Vue pour supprimer (désactiver) un compte utilisateur.
    Requiert le mot de passe actuel pour confirmation.
    """
    password = request.data.get('password')
    if not password:
        return Response(
            {'error': 'Le mot de passe est requis'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = request.user
    
    # Vérifier le mot de passe
    if not user.check_password(password):
        return Response(
            {'error': 'Mot de passe incorrect'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Désactiver le compte
        user.is_active = False
        # Ajouter un marqueur de suppression
        user.email = f"deleted_{user.email}"  # Pour permettre la réutilisation de l'email
        user.save()
        
        # Révoquer tous les tokens JWT de l'utilisateur
        RefreshToken.for_user(user)
        
        return Response(status=status.HTTP_204_NO_CONTENT)
        
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du compte: {str(e)}")
        return Response(
            {'error': 'Une erreur est survenue lors de la suppression du compte'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )