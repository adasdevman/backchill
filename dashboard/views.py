from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import Payment, Categorie, Annonce
from django.db.models import Count, Sum
from users.models import User
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

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

@login_required
def dashboard_home(request):
    logger.info("Starting dashboard_home view")
    
    # Récupérer les statistiques générales
    total_users = User.objects.count()
    total_annonces = Annonce.objects.count()
    total_reservations = Payment.objects.count()
    total_revenue = Payment.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0

    # Récupérer les catégories et le nombre d'annonces par catégorie
    try:
        categories = list(Categorie.objects.all().order_by('id'))
        logger.info(f"Found {len(categories)} categories")
        
        annonces_par_categorie = []
        for categorie in categories:
            count = Annonce.objects.filter(categorie=categorie).count()
            annonces_par_categorie.append(count)
            logger.info(f"Catégorie {categorie.nom} (ID: {categorie.id}): {count} annonces")

        # Vérifier si les données sont vides
        if not categories:
            logger.warning("No categories found in database")
        if not annonces_par_categorie:
            logger.warning("No announcements found for categories")

    except Exception as e:
        logger.error(f"Error while fetching categories: {str(e)}")
        categories = []
        annonces_par_categorie = []

    # Récupérer les données d'inscription des 30 derniers jours
    try:
        thirty_days_ago = timezone.now() - timedelta(days=30)
        inscriptions_par_jour = User.objects.filter(
            date_joined__gte=thirty_days_ago
        ).annotate(
            date=TruncDate('date_joined')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')

        dates = [entry['date'].strftime('%Y-%m-%d') for entry in inscriptions_par_jour]
        inscriptions = [entry['count'] for entry in inscriptions_par_jour]
        
        logger.info(f"Found {len(dates)} days of registration data")

    except Exception as e:
        logger.error(f"Error while fetching registration data: {str(e)}")
        dates = []
        inscriptions = []

    context = {
        'total_users': total_users,
        'total_annonces': total_annonces,
        'total_reservations': total_reservations,
        'total_revenue': total_revenue,
        'categories': categories,
        'annonces_par_categorie': annonces_par_categorie,
        'dates': dates,
        'inscriptions': inscriptions,
    }

    logger.info("Context prepared for dashboard template")
    logger.debug(f"Categories in context: {[c.nom for c in categories]}")
    logger.debug(f"Announcements counts: {annonces_par_categorie}")

    return render(request, 'dashboard/dashboard.html', context) 