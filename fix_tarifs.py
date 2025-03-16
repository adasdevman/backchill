import os
import django

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chillnowback.settings')
django.setup()

from core.models import Annonce, Tarif

def fix_tarifs():
    print("Correction des tarifs...")
    
    for annonce in Annonce.objects.all():
        print(f"\nTraitement de l'annonce: {annonce.titre}")
        
        # Supprimer tous les tarifs existants
        nb_deleted = annonce.tarifs.all().count()
        annonce.tarifs.all().delete()
        print(f"- {nb_deleted} anciens tarifs supprimés")
        
        # Créer les nouveaux tarifs
        Tarif.objects.create(
            annonce=annonce,
            nom="Entrée standard (FCFA)",
            prix=5000.00
        )
        Tarif.objects.create(
            annonce=annonce,
            nom="Tarif réduit (FCFA)",
            prix=3000.00
        )
        print("- 2 nouveaux tarifs ajoutés avec FCFA")

if __name__ == '__main__':
    print("Début de la correction des tarifs...")
    fix_tarifs()
    print("\nTerminé!") 