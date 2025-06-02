from rest_framework import serializers
from ..models import (
    Categorie, SousCategorie, Annonce, 
    Horaire, Tarif, GaleriePhoto, Payment, GalerieVideo
)
from .base import TimeStampedModelSerializer
from .categorie import CategorieSerializer, SousCategorieSerializer
from users.serializers import UserProfileSerializer
import datetime

class HoraireSerializer(serializers.ModelSerializer):
    heure_ouverture = serializers.SerializerMethodField()
    heure_fermeture = serializers.SerializerMethodField()

    class Meta:
        model = Horaire
        fields = ['id', 'jour', 'heure_ouverture', 'heure_fermeture']

    def get_heure_ouverture(self, obj):
        return obj.heure_ouverture.strftime('%H:%M')

    def get_heure_fermeture(self, obj):
        return obj.heure_fermeture.strftime('%H:%M')

class TarifSerializer(serializers.ModelSerializer):
    # Définir explicitement le champ prix pour le convertir correctement
    prix = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    
    class Meta:
        model = Tarif
        fields = ['id', 'nom', 'prix']

class GaleriePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GaleriePhoto
        fields = ['id', 'image']

class GalerieVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalerieVideo
        fields = ['id', 'video']

class AnnonceListSerializer(TimeStampedModelSerializer):
    categorie = CategorieSerializer(read_only=True)
    sous_categorie = SousCategorieSerializer(read_only=True)
    photos = GaleriePhotoSerializer(many=True, read_only=True)
    videos = GalerieVideoSerializer(many=True, read_only=True)  # Added this line
    categorie_nom = serializers.CharField(source='categorie.nom', read_only=True)
    sous_categorie_nom = serializers.CharField(source='sous_categorie.nom', read_only=True)
    horaires = HoraireSerializer(source='horaire_set', many=True, read_only=True)
    tarifs = TarifSerializer(many=True, read_only=True)
    annonceur = UserProfileSerializer(source='utilisateur', read_only=True)
    status = serializers.CharField(read_only=True)
    date_evenement = serializers.SerializerMethodField()
    heure_evenement = serializers.SerializerMethodField()
    
    def get_date_evenement(self, obj):
        """
        Convertit explicitement une date ou un datetime en string au format YYYY-MM-DD
        """
        if obj.date_evenement is None:
            return None
        if isinstance(obj.date_evenement, datetime.datetime):
            return obj.date_evenement.date().isoformat()
        return obj.date_evenement.isoformat() if obj.date_evenement else None
    
    def get_heure_evenement(self, obj):
        """
        Extrait l'heure si date_evenement est un datetime, sinon retourne None
        """
        if obj.date_evenement is None:
            return None
        if isinstance(obj.date_evenement, datetime.datetime):
            return obj.date_evenement.strftime('%H:%M')
        return None
        
    class Meta:
        model = Annonce
        fields = [
            'id', 'titre', 'description', 'localisation',
            'date_evenement', 'heure_evenement', 'est_actif', 'categorie',
            'sous_categorie', 'photos', 'videos', 'categorie_nom',  # Added 'videos'
            'sous_categorie_nom', 'horaires', 'tarifs',
            'created', 'modified', 'annonceur', 'status'
        ]

class AnnonceSerializer(TimeStampedModelSerializer):
    photos = serializers.ListField(
        child=serializers.URLField(), write_only=True, required=False
    )
    videos = serializers.ListField(
        child=serializers.URLField(), write_only=True, required=False
    )
    horaires = HoraireSerializer(source='horaire_set', many=True, read_only=True)
    tarifs = TarifSerializer(many=True, read_only=True)
    annonceur = UserProfileSerializer(source='utilisateur', read_only=True)
    categorie = CategorieSerializer(read_only=True)
    sous_categorie = SousCategorieSerializer(read_only=True)
    deleted_images = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)
    heure_evenement = serializers.SerializerMethodField()
    
    # Explicitly declare all fields
    titre = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    localisation = serializers.CharField(required=True)
    date_evenement = serializers.SerializerMethodField()
    est_actif = serializers.BooleanField(default=True)
    status = serializers.CharField(default='PENDING')
    
    def get_date_evenement(self, obj):
        """
        Convertit explicitement une date ou un datetime en string au format YYYY-MM-DD
        """
        if obj.date_evenement is None:
            return None
        if isinstance(obj.date_evenement, datetime.datetime):
            return obj.date_evenement.date().isoformat()
        return obj.date_evenement.isoformat() if obj.date_evenement else None
    
    def get_heure_evenement(self, obj):
        """
        Extrait l'heure si date_evenement est un datetime, sinon retourne None
        """
        if obj.date_evenement is None:
            return None
        if isinstance(obj.date_evenement, datetime.datetime):
            return obj.date_evenement.strftime('%H:%M')
        return None
        
    class Meta:
        model = Annonce
        fields = [
            'id', 'titre', 'description', 'localisation',
            'date_evenement', 'heure_evenement', 'est_actif', 'categorie_id',
            'sous_categorie_id', 'categorie', 'sous_categorie',
            'photos', 'videos', 'horaires', 'tarifs', 'annonceur',  # Added 'videos' and made photos/videos writable
            'created', 'modified', 'status', 'deleted_images'
        ]
        read_only_fields = ['utilisateur', 'categorie', 'sous_categorie', 'annonceur']


    def create(self, validated_data):
        photos_data = validated_data.pop('photos', [])
        videos_data = validated_data.pop('videos', [])
        # Ensure the user is set from the context
        validated_data['utilisateur'] = self.context['request'].user
        
        # Create the instance
        instance = super().create(validated_data)

        for photo_url in photos_data:
            GaleriePhoto.objects.create(annonce=instance, image=photo_url)
        for video_url in videos_data:
            GalerieVideo.objects.create(annonce=instance, video=video_url)
        
        # Handle horaires if present in the initial data
        horaires_data = self.initial_data.get('horaires', [])
        for horaire_data in horaires_data:
            Horaire.objects.create(
                annonce=instance,
                jour=horaire_data['jour'],
                heure_ouverture=horaire_data['heure_ouverture'],
                heure_fermeture=horaire_data['heure_fermeture']
            )
        
        # Handle tarifs if present in the initial data
        tarifs_data = self.initial_data.get('tarifs', [])
        for tarif_data in tarifs_data:
            try:
                # Convertir explicitement la chaîne en décimal
                prix_str = tarif_data['prix']
                # Remplacer les virgules par des points si présentes
                prix_str = prix_str.replace(',', '.')
                prix_decimal = float(prix_str)
                
                Tarif.objects.create(
                    annonce=instance,
                    nom=tarif_data['nom'],
                    prix=prix_decimal
                )
            except (ValueError, TypeError) as e:
                print(f"Erreur lors de la conversion du prix '{tarif_data.get('prix')}': {str(e)}")
                # Utiliser une valeur par défaut en cas d'erreur
                Tarif.objects.create(
                    annonce=instance,
                    nom=tarif_data['nom'],
                    prix=0.0
                )
            except Exception as e:
                print(f"Erreur inattendue lors de la création du tarif: {str(e)}")
        
        return instance

    def update(self, instance, validated_data):
        photos_data = validated_data.pop('photos', [])
        videos_data = validated_data.pop('videos', [])

        # Gérer les images supprimées
        deleted_images = self.initial_data.get('deleted_images', [])
        if deleted_images:
            for image_url in deleted_images:
                try:
                    # Extraire le nom du fichier de l'URL
                    image_name = image_url.split('/')[-1]
                    photos = instance.photos.filter(image__contains=image_name)
                    for photo in photos:
                        photo.delete()  # Ceci appellera la méthode delete personnalisée
                except Exception as e:
                    print(f"Erreur lors de la suppression de l'image {image_url}: {str(e)}")
                    continue

        # Clear existing photos and videos if new ones are provided
        if photos_data:
            instance.photos.all().delete()
        for photo_url in photos_data:
            GaleriePhoto.objects.create(annonce=instance, image=photo_url)
        
        if videos_data:
            instance.videos.all().delete()
        for video_url in videos_data:
            GalerieVideo.objects.create(annonce=instance, video=video_url)

        # Gérer les tarifs s'ils sont présents dans les données
        tarifs_data = self.initial_data.get('tarifs', [])
        if tarifs_data:
            # Supprimer les tarifs existants
            instance.tarifs.all().delete()
            
            # Créer les nouveaux tarifs avec conversion explicite de prix
            for tarif_data in tarifs_data:
                try:
                    # Convertir explicitement la chaîne en décimal
                    prix_str = tarif_data['prix']
                    # Remplacer les virgules par des points si présentes
                    prix_str = prix_str.replace(',', '.')
                    prix_decimal = float(prix_str)
                    
                    Tarif.objects.create(
                        annonce=instance,
                        nom=tarif_data['nom'],
                        prix=prix_decimal
                    )
                except (ValueError, TypeError) as e:
                    print(f"Erreur lors de la conversion du prix '{tarif_data.get('prix')}': {str(e)}")
                    # Utiliser une valeur par défaut en cas d'erreur
                    Tarif.objects.create(
                        annonce=instance,
                        nom=tarif_data['nom'],
                        prix=0.0
                    )
                except Exception as e:
                    print(f"Erreur inattendue lors de la création du tarif: {str(e)}")
                
        # Gérer les horaires s'ils sont présents dans les données
        horaires_data = self.initial_data.get('horaires', [])
        if horaires_data:
            # Supprimer les horaires existants
            instance.horaire_set.all().delete()
            
            # Créer les nouveaux horaires
            for horaire_data in horaires_data:
                Horaire.objects.create(
                    annonce=instance,
                    jour=horaire_data['jour'],
                    heure_ouverture=horaire_data['heure_ouverture'],
                    heure_fermeture=horaire_data['heure_fermeture']
                )

        # Mettre à jour les autres champs
        instance = super().update(instance, validated_data)
        return instance

class AnnonceDetailSerializer(TimeStampedModelSerializer):
    categorie = CategorieSerializer(read_only=True)
    sous_categorie = SousCategorieSerializer(read_only=True)
    horaires = HoraireSerializer(source='horaire_set', many=True, read_only=True)
    tarifs = TarifSerializer(many=True, read_only=True)
    photos = GaleriePhotoSerializer(many=True, read_only=True) # Keep read_only for detail view if it's just for display
    videos = GalerieVideoSerializer(many=True, read_only=True) # Add videos here
    annonceur = UserProfileSerializer(source='utilisateur', read_only=True)
    status = serializers.CharField(read_only=True)
    date_evenement = serializers.SerializerMethodField()
    heure_evenement = serializers.SerializerMethodField()
    
    def get_date_evenement(self, obj):
        """
        Convertit explicitement une date ou un datetime en string au format YYYY-MM-DD
        """
        if obj.date_evenement is None:
            return None
        if isinstance(obj.date_evenement, datetime.datetime):
            return obj.date_evenement.date().isoformat()
        return obj.date_evenement.isoformat() if obj.date_evenement else None
    
    def get_heure_evenement(self, obj):
        """
        Extrait l'heure si date_evenement est un datetime, sinon retourne None
        """
        if obj.date_evenement is None:
            return None
        if isinstance(obj.date_evenement, datetime.datetime):
            return obj.date_evenement.strftime('%H:%M')
        return None

    class Meta:
        model = Annonce
        fields = [
            'id', 'utilisateur', 'categorie', 'sous_categorie',
            'titre', 'description', 'localisation', 'date_evenement',
            'heure_evenement', 'est_actif', 'horaires', 'tarifs', 'photos',
            'videos',  # Added videos
            'created', 'modified', 'annonceur', 'status'
        ]
        read_only_fields = ['utilisateur']

