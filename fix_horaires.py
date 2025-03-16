import os
import django
from django.utils import timezone

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chillnowback.settings')
django.setup()

from core.models import Annonce, Horaire

def fix_horaires():
    print("Correction des horaires des lieux...")
    
    # Récupérer tous les lieux (annonces sans date_evenement)
    lieux = Annonce.objects.filter(date_evenement__isnull=True)
    
    for lieu in lieux:
        print(f"\nTraitement du lieu: {lieu.titre}")
        
        # Supprimer tous les horaires existants
        nb_deleted = lieu.horaire_set.all().count()
        lieu.horaire_set.all().delete()
        print(f"- {nb_deleted} anciens horaires supprimés")
        
        # Créer les nouveaux horaires
        # Horaires semaine
        jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi']
        for jour in jours:
            Horaire.objects.create(
                annonce=lieu,
                jour=jour,
                heure_ouverture=timezone.datetime.strptime('09:00', '%H:%M').time(),
                heure_fermeture=timezone.datetime.strptime('18:00', '%H:%M').time()
            )
        
        # Horaires weekend
        for jour in ['Samedi', 'Dimanche']:
            Horaire.objects.create(
                annonce=lieu,
                jour=jour,
                heure_ouverture=timezone.datetime.strptime('10:00', '%H:%M').time(),
                heure_fermeture=timezone.datetime.strptime('16:00', '%H:%M').time()
            )
        print("- 7 nouveaux horaires ajoutés")

if __name__ == '__main__':
    print("Début de la correction des horaires...")
    fix_horaires()
    print("\nTerminé!") 