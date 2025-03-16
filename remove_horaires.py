import os
import django

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chillnowback.settings')
django.setup()

from core.models import Horaire, Annonce

def remove_horaires_events():
    print("Suppression des horaires des événements...")
    # Récupérer tous les événements (annonces avec date_evenement)
    events = Annonce.objects.exclude(date_evenement__isnull=True)
    count = 0
    
    for event in events:
        # Supprimer les horaires de cet événement
        nb_deleted = event.horaire_set.all().count()
        event.horaire_set.all().delete()
        count += nb_deleted
        print(f"Horaires supprimés pour l'événement: {event.titre}")
    
    print(f"{count} horaires d'événements ont été supprimés.")

if __name__ == '__main__':
    remove_horaires_events()
    print("Terminé!") 