import os
import django
from django.utils import timezone

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chillnowback.settings')
django.setup()

from core.models import Annonce, Tarif, Horaire

def add_tarifs_horaires():
    # Pour chaque annonce existante
    for annonce in Annonce.objects.all():
        print(f"Traitement de l'annonce: {annonce.titre}")
        
        # Ajouter des tarifs
        Tarif.objects.create(
            annonce=annonce,
            nom="Entrée standard",
            prix=5000.00  # 5000 FCFA
        )
        Tarif.objects.create(
            annonce=annonce,
            nom="Tarif réduit",
            prix=3000.00  # 3000 FCFA
        )
        
        # Ajouter des horaires seulement si ce n'est pas un événement
        if not annonce.date_evenement:
            print(f"Ajout des horaires pour le lieu: {annonce.titre}")
            # Ajouter des horaires semaine
            jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi']
            for jour in jours:
                Horaire.objects.create(
                    annonce=annonce,
                    jour=jour,
                    heure_ouverture=timezone.datetime.strptime('09:00', '%H:%M').time(),
                    heure_fermeture=timezone.datetime.strptime('18:00', '%H:%M').time()
                )
            
            # Horaires weekend
            for jour in ['Samedi', 'Dimanche']:
                Horaire.objects.create(
                    annonce=annonce,
                    jour=jour,
                    heure_ouverture=timezone.datetime.strptime('10:00', '%H:%M').time(),
                    heure_fermeture=timezone.datetime.strptime('16:00', '%H:%M').time()
                )
        else:
            print(f"Pas d'horaires ajoutés car c'est un événement: {annonce.titre}")
        
        print(f"Ajout des tarifs et horaires terminé pour: {annonce.titre}")

if __name__ == '__main__':
    print("Début de l'ajout des tarifs et horaires...")
    add_tarifs_horaires()
    print("Terminé!") 