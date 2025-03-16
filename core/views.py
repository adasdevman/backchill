from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from django.utils import timezone
from users.models import User
from .models import (
    Annonce, Categorie, SousCategorie, 
    Horaire, Tarif, GaleriePhoto, Payment
)
from .serializers import (
    AnnonceDetailSerializer,
    AnnonceListSerializer,
    CategorieSerializer,
    PaymentSerializer
)
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

@login_required
def dashboard_home(request):
    total_users = User.objects.count()
    total_annonces = Annonce.objects.count()
    total_payments = Payment.objects.count()
    
    # Données pour les graphiques
    stats_categories = Annonce.objects.values('categorie').annotate(total=Count('id'))
    stats_payments = Payment.objects.values('status').annotate(total=Count('id'))
    
    context = {
        'total_users': total_users,
        'total_annonces': total_annonces,
        'total_payments': total_payments,
        'stats_categories': stats_categories,
        'stats_payments': stats_payments,
    }
    return render(request, 'dashboard/home.html', context)

def dashboard_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard:home')
        else:
            messages.error(request, 'Identifiants invalides')
    return render(request, 'dashboard/login.html')

@login_required
def dashboard_logout(request):
    logout(request)
    return redirect('dashboard:login')

@login_required
def user_list(request):
    # Récupérer le terme de recherche
    search_query = request.GET.get('search', '')
    
    # Filtrer les utilisateurs
    users_list = User.objects.all().order_by('-date_joined')
    if search_query:
        users_list = users_list.filter(
            username__icontains=search_query
        ) | users_list.filter(
            email__icontains=search_query
        ) | users_list.filter(
            first_name__icontains=search_query
        ) | users_list.filter(
            last_name__icontains=search_query
        ) | users_list.filter(
            role__icontains=search_query
        )
    
    # Pagination
    paginator = Paginator(users_list, 10)  # 10 utilisateurs par page
    page = request.GET.get('page')
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    
    return render(request, 'dashboard/users.html', {
        'users': users,
        'search_query': search_query,
        'total_users': users_list.count()
    })

@login_required
def user_create(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role', '').upper()
        phone_number = request.POST.get('telephone')
        
        try:
            user = User.objects.create_user(
                email=email,
                password=password,
                role=role,
                phone_number=phone_number
            )
            messages.success(request, 'Utilisateur créé avec succès')
            return redirect('dashboard:users')
        except Exception as e:
            messages.error(request, f'Erreur lors de la création: {str(e)}')
    
    return render(request, 'dashboard/user_form.html', {'action': 'Créer'})

@login_required
def user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        try:
            user.username = request.POST.get('username')
            user.email = request.POST.get('email')
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.role = request.POST.get('role', '').upper()
            user.phone_number = request.POST.get('telephone')
            
            password = request.POST.get('password')
            if password:
                user.set_password(password)
            
            user.save()
            messages.success(request, 'Utilisateur modifié avec succès')
            return redirect('dashboard:users')
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification: {str(e)}')
    
    return render(request, 'dashboard/user_form.html', {
        'user': user,
        'action': 'Modifier'
    })

@login_required
def user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Utilisateur supprimé avec succès')
        return redirect('dashboard:users')
    return render(request, 'dashboard/user_confirm_delete.html', {'user': user})

@login_required
def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'dashboard/user_detail.html', {'user': user})

@login_required
def annonce_list(request):
    # Récupérer le terme de recherche
    search_query = request.GET.get('search', '')
    
    # Filtrer les annonces
    annonces_list = Annonce.objects.all().order_by('-created')
    if search_query:
        annonces_list = annonces_list.filter(
            titre__icontains=search_query
        ) | annonces_list.filter(
            description__icontains=search_query
        ) | annonces_list.filter(
            localisation__icontains=search_query
        ) | annonces_list.filter(
            categorie__nom__icontains=search_query
        ) | annonces_list.filter(
            sous_categorie__nom__icontains=search_query
        )
    
    # Pagination
    paginator = Paginator(annonces_list, 10)  # 10 annonces par page
    page = request.GET.get('page')
    try:
        annonces = paginator.page(page)
    except PageNotAnInteger:
        annonces = paginator.page(1)
    except EmptyPage:
        annonces = paginator.page(paginator.num_pages)
    
    return render(request, 'dashboard/annonces.html', {
        'annonces': annonces,
        'search_query': search_query,
        'total_annonces': annonces_list.count()
    })

@login_required
def annonce_create(request):
    if request.method == 'POST':
        try:
            # Récupération des données de base
            categorie = request.POST.get('categorie', '').upper()  # Conversion en majuscules
            sous_categorie = request.POST.get('sous_categorie', '').upper()  # Conversion en majuscules
            titre = request.POST.get('titre')
            description = request.POST.get('description')
            localisation = request.POST.get('localisation')
            
            # Validation des champs obligatoires
            if not all([categorie, sous_categorie, titre, description, localisation]):
                messages.error(request, 'Tous les champs obligatoires doivent être remplis')
                return render(request, 'dashboard/annonce_form.html', {'action': 'Créer', 'error': 'Champs obligatoires manquants'})

            # Gestion de la date d'événement pour la catégorie EVENT
            date_evenement = None
            if categorie == 'EVENT':
                event_date = request.POST.get('event_date')
                event_time = request.POST.get('event_time')
                if not event_date or not event_time:
                    messages.error(request, 'La date et l\'heure sont requises pour un événement')
                    return render(request, 'dashboard/annonce_form.html', {'action': 'Créer', 'error': 'Date et heure requises'})
                date_evenement = f"{event_date} {event_time}"

            # Création de l'annonce
            annonce = Annonce.objects.create(
                utilisateur=request.user,
                categorie=get_object_or_404(Categorie, nom=categorie),
                sous_categorie=get_object_or_404(SousCategorie, nom=sous_categorie),
                titre=titre,
                description=description,
                localisation=localisation,
                date_evenement=date_evenement
            )

            # Gestion des horaires
            jours = request.POST.getlist('jour[]')
            heures_ouverture = request.POST.getlist('heure_ouverture[]')
            heures_fermeture = request.POST.getlist('heure_fermeture[]')
            
            for jour, ouverture, fermeture in zip(jours, heures_ouverture, heures_fermeture):
                if jour and ouverture and fermeture:
                    Horaire.objects.create(
                        annonce=annonce,
                        jour=jour,
                        heure_ouverture=ouverture,
                        heure_fermeture=fermeture
                    )

            # Gestion des tarifs
            noms_tarif = request.POST.getlist('nom_tarif[]')
            prix_tarif = request.POST.getlist('prix_tarif[]')
            
            for nom, prix in zip(noms_tarif, prix_tarif):
                if nom and prix:
                    Tarif.objects.create(
                        annonce=annonce,
                        nom=nom,
                        prix=prix
                    )

            # Gestion des photos
            photos = request.FILES.getlist('galerie_photo')
            for photo in photos:
                GaleriePhoto.objects.create(
                    annonce=annonce,
                    image=photo
                )

            messages.success(request, 'Annonce créée avec succès')
            return redirect('dashboard:annonces')

        except Exception as e:
            logger.error(f"Erreur lors de la création de l'annonce: {str(e)}")
            messages.error(request, f"Une erreur s'est produite: {str(e)}")
            return render(request, 'dashboard/annonce_form.html', {'action': 'Créer', 'error': str(e)})

    # Récupérer les catégories et sous-catégories pour le formulaire
    categories = Categorie.objects.all()
    context = {
        'action': 'Créer',
        'categories': categories
    }
    return render(request, 'dashboard/annonce_form.html', context)

@login_required
def annonce_edit(request, annonce_id):
    annonce = get_object_or_404(Annonce, id=annonce_id)
    categories = Categorie.objects.all()
    sous_categories = SousCategorie.objects.filter(categorie=annonce.categorie)
    
    if request.method == 'POST':
        try:
            # Récupération des données de base
            categorie = request.POST.get('categorie', '').upper()
            sous_categorie = request.POST.get('sous_categorie', '').upper()
            titre = request.POST.get('titre')
            description = request.POST.get('description')
            localisation = request.POST.get('localisation')
            
            # Validation des champs obligatoires
            if not all([categorie, sous_categorie, titre, description, localisation]):
                messages.error(request, 'Tous les champs obligatoires doivent être remplis')
                return render(request, 'dashboard/annonce_form.html', {
                    'action': 'Modifier',
                    'annonce': annonce,
                    'categories': categories,
                    'sous_categories': sous_categories,
                    'error': 'Champs obligatoires manquants'
                })

            # Mise à jour de l'annonce
            annonce.categorie = get_object_or_404(Categorie, nom=categorie)
            annonce.sous_categorie = get_object_or_404(SousCategorie, nom=sous_categorie)
            annonce.titre = titre
            annonce.description = description
            annonce.localisation = localisation
            
            # Mise à jour du statut
            status = request.POST.get('status')
            if status in ['PENDING', 'ACTIVE', 'INACTIVE']:
                annonce.status = status

            # Gestion de la date d'événement pour la catégorie EVENT
            if categorie == 'EVENT':
                event_date = request.POST.get('event_date')
                event_time = request.POST.get('event_time')
                if not event_date or not event_time:
                    messages.error(request, 'La date et l\'heure sont requises pour un événement')
                    return render(request, 'dashboard/annonce_form.html', {
                        'action': 'Modifier',
                        'annonce': annonce,
                        'categories': categories,
                        'sous_categories': sous_categories,
                        'error': 'Date et heure requises'
                    })
                annonce.date_evenement = f"{event_date} {event_time}"
            else:
                annonce.date_evenement = None

            annonce.save()

            # Gestion de la suppression des photos
            photos_a_supprimer = request.POST.getlist('delete_photos')
            if photos_a_supprimer:
                GaleriePhoto.objects.filter(id__in=photos_a_supprimer).delete()

            # Ajout de nouvelles photos
            photos = request.FILES.getlist('galerie_photo')
            for photo in photos:
                GaleriePhoto.objects.create(
                    annonce=annonce,
                    image=photo
                )

            # Mise à jour des horaires
            annonce.horaire_set.all().delete()
            jours = request.POST.getlist('jour[]')
            heures_ouverture = request.POST.getlist('heure_ouverture[]')
            heures_fermeture = request.POST.getlist('heure_fermeture[]')
            
            for jour, ouverture, fermeture in zip(jours, heures_ouverture, heures_fermeture):
                if jour and ouverture and fermeture:
                    Horaire.objects.create(
                        annonce=annonce,
                        jour=jour,
                        heure_ouverture=ouverture,
                        heure_fermeture=fermeture
                    )

            # Mise à jour des tarifs
            annonce.tarifs.all().delete()
            noms_tarif = request.POST.getlist('nom_tarif[]')
            prix_tarif = request.POST.getlist('prix_tarif[]')
            
            for nom, prix in zip(noms_tarif, prix_tarif):
                if nom and prix:
                    Tarif.objects.create(
                        annonce=annonce,
                        nom=nom,
                        prix=prix
                    )

            messages.success(request, 'Annonce modifiée avec succès')
            return redirect('dashboard:annonces')

        except Exception as e:
            logger.error(f"Erreur lors de la modification de l'annonce: {str(e)}")
            messages.error(request, f"Une erreur s'est produite: {str(e)}")
            return render(request, 'dashboard/annonce_form.html', {
                'action': 'Modifier',
                'annonce': annonce,
                'categories': categories,
                'sous_categories': sous_categories,
                'error': str(e)
            })

    return render(request, 'dashboard/annonce_form.html', {
        'annonce': annonce,
        'categories': categories,
        'sous_categories': sous_categories,
        'action': 'Modifier'
    })

@login_required
def annonce_delete(request, annonce_id):
    annonce = get_object_or_404(Annonce, id=annonce_id)
    if request.method == 'POST':
        annonce.delete()
        messages.success(request, 'Annonce supprimée avec succès')
        return redirect('dashboard:annonces')
    return render(request, 'dashboard/annonce_confirm_delete.html', {'annonce': annonce})

@login_required
def annonce_detail(request, annonce_id):
    annonce = get_object_or_404(Annonce, id=annonce_id)
    return render(request, 'dashboard/annonce_detail.html', {'annonce': annonce})

@login_required
def statistiques(request):
    # Statistiques par catégorie avec les noms au lieu des IDs
    stats_categories = Annonce.objects.values('categorie__nom').annotate(total=Count('id')).values('categorie__nom', 'total')
    
    # Statistiques des paiements
    stats_payments = Payment.objects.values('status').annotate(total=Count('id'))
    
    context = {
        'stats_categories': stats_categories,
        'stats_payments': stats_payments,
    }
    return render(request, 'dashboard/statistiques.html', context)

@login_required
def annonce_duplicate(request, annonce_id):
    original_annonce = get_object_or_404(Annonce, id=annonce_id)
    
    # Créer une nouvelle annonce avec les mêmes données
    new_annonce = Annonce.objects.create(
        utilisateur=request.user,
        categorie=original_annonce.categorie,
        sous_categorie=original_annonce.sous_categorie,
        titre=f"Copie de {original_annonce.titre}",
        description=original_annonce.description,
        localisation=original_annonce.localisation,
        date_evenement=original_annonce.date_evenement
    )
    
    # Dupliquer les horaires
    for horaire in original_annonce.horaire_set.all():
        Horaire.objects.create(
            annonce=new_annonce,
            jour=horaire.jour,
            heure_ouverture=horaire.heure_ouverture,
            heure_fermeture=horaire.heure_fermeture
        )
    
    # Dupliquer les tarifs
    for tarif in original_annonce.tarifs.all():
        Tarif.objects.create(
            annonce=new_annonce,
            nom=tarif.nom,
            prix=tarif.prix
        )
    
    # Dupliquer les photos
    for photo in original_annonce.photos.all():
        GaleriePhoto.objects.create(
            annonce=new_annonce,
            image=photo.image
        )
    
    messages.success(request, 'Annonce dupliquée avec succès')
    return redirect('dashboard:annonce_edit', new_annonce.id)

@login_required
def payment_list(request):
    payments = Payment.objects.all().order_by('-created')
    return render(request, 'dashboard/payments/list.html', {'payments': payments})

@login_required
def payment_detail(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    return render(request, 'dashboard/payments/detail.html', {'payment': payment})

@login_required
def payment_edit(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        payment.status = request.POST.get('status')
        payment.amount = request.POST.get('amount')
        payment.payment_type = request.POST.get('payment_type')
        payment.description = request.POST.get('description')
        payment.save()
        
        messages.success(request, 'Paiement mis à jour avec succès.')
        return redirect('dashboard:payment_detail', payment_id=payment.id)
    
    return render(request, 'dashboard/payments/edit.html', {'payment': payment})

@login_required
def payment_delete(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        payment.delete()
        messages.success(request, 'Paiement supprimé avec succès.')
        return redirect('dashboard:payments')
    
    return redirect('dashboard:payment_detail', payment_id=payment.id)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mes_annonces(request):
    """Récupère les annonces créées par l'utilisateur connecté"""
    annonces = Annonce.objects.filter(
        createur=request.user
    ).order_by('-created')
    serializer = AnnonceListSerializer(annonces, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mes_chills(request):
    """Récupère les chills (places to be) de l'utilisateur"""
    chills = Annonce.objects.filter(
        categorie__nom='Place to be',
        favoris=request.user
    ).order_by('-created')
    serializer = AnnonceListSerializer(chills, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mes_tickets(request):
    """Récupère les tickets (événements) de l'utilisateur"""
    tickets = Annonce.objects.filter(
        categorie__nom='Événement',
        reservations__utilisateur=request.user
    ).order_by('-created')
    serializer = AnnonceListSerializer(tickets, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def annonces_publiques(request):
    """Récupère toutes les annonces publiques"""
    annonces = Annonce.objects.all().order_by('-created')
    
    # Filtrage par catégorie si spécifié
    categorie = request.GET.get('categorie')
    if categorie:
        annonces = annonces.filter(categorie__nom=categorie)
    
    # Filtrage par sous-catégorie si spécifié
    sous_categorie = request.GET.get('sous_categorie')
    if sous_categorie:
        annonces = annonces.filter(sous_categorie__nom=sous_categorie)
    
    serializer = AnnonceListSerializer(annonces, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def annonce_detail_public(request, annonce_id):
    """Récupère les détails d'une annonce publique"""
    annonce = get_object_or_404(Annonce, id=annonce_id)
    serializer = AnnonceDetailSerializer(annonce)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def categories(request):
    """Récupère toutes les catégories avec leurs sous-catégories"""
    categories = Categorie.objects.all().order_by('ordre')
    serializer = CategorieSerializer(categories, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def annonces_par_categorie(request):
    """Récupère les annonces filtrées par catégorie et sous-catégorie"""
    categorie_id = request.GET.get('categorie')
    sous_categorie_id = request.GET.get('sous_categorie')
    
    annonces = Annonce.objects.all()
    if categorie_id:
        annonces = annonces.filter(categorie_id=categorie_id)
    if sous_categorie_id:
        annonces = annonces.filter(sous_categorie_id=sous_categorie_id)
        
    serializer = AnnonceListSerializer(annonces, many=True)
    return Response(serializer.data)
