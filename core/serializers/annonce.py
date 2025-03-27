from rest_framework import serializers
from ..models import (
    Categorie, SousCategorie, Annonce, 
    Horaire, Tarif, GaleriePhoto, Payment
)
from .base import TimeStampedModelSerializer
from .categorie import CategorieSerializer, SousCategorieSerializer
from users.serializers import UserProfileSerializer

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
    class Meta:
        model = Tarif
        fields = ['id', 'nom', 'prix']

class GaleriePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GaleriePhoto
        fields = ['id', 'image']

class AnnonceListSerializer(TimeStampedModelSerializer):
    categorie = CategorieSerializer(read_only=True)
    sous_categorie = SousCategorieSerializer(read_only=True)
    photos = GaleriePhotoSerializer(many=True, read_only=True)
    categorie_nom = serializers.CharField(source='categorie.nom', read_only=True)
    sous_categorie_nom = serializers.CharField(source='sous_categorie.nom', read_only=True)
    horaires = HoraireSerializer(source='horaire_set', many=True, read_only=True)
    tarifs = TarifSerializer(many=True, read_only=True)
    annonceur = UserProfileSerializer(source='utilisateur', read_only=True)
    status = serializers.CharField(read_only=True)
    date_evenement = serializers.DateField(format='%Y-%m-%d', read_only=True)

    class Meta:
        model = Annonce
        fields = [
            'id', 'titre', 'description', 'localisation',
            'date_evenement', 'est_actif', 'categorie',
            'sous_categorie', 'photos', 'categorie_nom',
            'sous_categorie_nom', 'horaires', 'tarifs',
            'created', 'modified', 'annonceur', 'status'
        ]

class AnnonceSerializer(TimeStampedModelSerializer):
    photos = GaleriePhotoSerializer(many=True, read_only=True)
    horaires = HoraireSerializer(source='horaire_set', many=True, read_only=True)
    tarifs = TarifSerializer(many=True, read_only=True)
    annonceur = UserProfileSerializer(source='utilisateur', read_only=True)
    categorie = CategorieSerializer(read_only=True)
    sous_categorie = SousCategorieSerializer(read_only=True)
    deleted_images = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)
    
    # Explicitly declare all fields
    titre = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    localisation = serializers.CharField(required=True)
    date_evenement = serializers.DateField(format='%Y-%m-%d', required=False, allow_null=True)
    est_actif = serializers.BooleanField(default=True)
    status = serializers.CharField(default='PENDING')

    class Meta:
        model = Annonce
        fields = [
            'id', 'titre', 'description', 'localisation',
            'date_evenement', 'est_actif', 'categorie_id',
            'sous_categorie_id', 'categorie', 'sous_categorie',
            'photos', 'horaires', 'tarifs', 'annonceur',
            'created', 'modified', 'status', 'deleted_images'
        ]
        read_only_fields = ['utilisateur']

    def validate(self, data):
        # Get category and subcategory IDs from the request data
        categorie_id = self.initial_data.get('categorie_id')
        sous_categorie_id = self.initial_data.get('sous_categorie_id')

        if not categorie_id:
            raise serializers.ValidationError({'categorie_id': 'Ce champ est obligatoire.'})
        if not sous_categorie_id:
            raise serializers.ValidationError({'sous_categorie_id': 'Ce champ est obligatoire.'})

        try:
            categorie = Categorie.objects.get(id=categorie_id)
            data['categorie'] = categorie
        except Categorie.DoesNotExist:
            raise serializers.ValidationError({'categorie_id': 'Catégorie invalide'})

        try:
            sous_categorie = SousCategorie.objects.get(
                id=sous_categorie_id,
                categorie=categorie
            )
            data['sous_categorie'] = sous_categorie
        except SousCategorie.DoesNotExist:
            raise serializers.ValidationError({'sous_categorie_id': 'Sous-catégorie invalide'})

        # Set default status if not provided
        if 'status' not in data:
            data['status'] = 'PENDING'

        return data

    def create(self, validated_data):
        # Ensure the user is set from the context
        validated_data['utilisateur'] = self.context['request'].user
        
        # Create the instance
        instance = super().create(validated_data)
        
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
            Tarif.objects.create(
                annonce=instance,
                nom=tarif_data['nom'],
                prix=tarif_data['prix']
            )
        
        return instance

    def update(self, instance, validated_data):
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

        # Mettre à jour les autres champs
        instance = super().update(instance, validated_data)
        return instance

class AnnonceDetailSerializer(TimeStampedModelSerializer):
    categorie = CategorieSerializer(read_only=True)
    sous_categorie = SousCategorieSerializer(read_only=True)
    horaires = HoraireSerializer(source='horaire_set', many=True, read_only=True)
    tarifs = TarifSerializer(many=True, read_only=True)
    photos = GaleriePhotoSerializer(many=True, read_only=True)
    annonceur = UserProfileSerializer(source='utilisateur', read_only=True)
    status = serializers.CharField(read_only=True)
    date_evenement = serializers.DateField(format='%Y-%m-%d', read_only=True)

    class Meta:
        model = Annonce
        fields = [
            'id', 'utilisateur', 'categorie', 'sous_categorie',
            'titre', 'description', 'localisation', 'date_evenement',
            'est_actif', 'horaires', 'tarifs', 'photos',
            'created', 'modified', 'annonceur', 'status'
        ]
        read_only_fields = ['utilisateur']

