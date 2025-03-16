from django.db import migrations
from django.utils import timezone

def add_tarifs_horaires(apps, schema_editor):
    Annonce = apps.get_model('core', 'Annonce')
    Tarif = apps.get_model('core', 'Tarif')
    Horaire = apps.get_model('core', 'Horaire')
    
    # Pour chaque annonce existante
    for annonce in Annonce.objects.all():
        # Ajouter des tarifs
        Tarif.objects.create(
            annonce=annonce,
            nom="Entrée standard",
            prix=15.00
        )
        Tarif.objects.create(
            annonce=annonce,
            nom="Tarif réduit",
            prix=10.00
        )
        
        # Ajouter des horaires
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

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),  # Assurez-vous que ceci pointe vers votre dernière migration
    ]

    operations = [
        migrations.RunPython(add_tarifs_horaires),
    ] 