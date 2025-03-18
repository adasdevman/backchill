from django.db import models
from django.conf import settings
from .base import TimeStampedModel
from django.utils import timezone

class Categorie(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    ordre = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['ordre', 'nom']
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'

    def __str__(self):
        return self.nom

class SousCategorie(models.Model):
    categorie = models.ForeignKey(
        Categorie, 
        on_delete=models.CASCADE,
        related_name='sous_categories'
    )
    nom = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    ordre = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['categorie', 'ordre', 'nom']
        verbose_name = 'Sous-catégorie'
        verbose_name_plural = 'Sous-catégories'
        unique_together = ['categorie', 'nom']

    def __str__(self):
        return f"{self.categorie.nom} - {self.nom}"

class Annonce(TimeStampedModel):
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('PENDING', 'En attente'),
        ('INACTIVE', 'Inactive'),
    )

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='core_annonces'
    )
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.PROTECT,
        related_name='annonces'
    )
    sous_categorie = models.ForeignKey(
        SousCategorie,
        on_delete=models.PROTECT,
        related_name='annonces'
    )
    titre = models.CharField(max_length=200)
    description = models.TextField()
    localisation = models.TextField()
    date_evenement = models.DateTimeField(null=True, blank=True)
    est_actif = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    favoris = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='core_annonces_favorites',
        blank=True
    )

    class Meta:
        ordering = ['-created']
        verbose_name = 'Annonce'
        verbose_name_plural = 'Annonces'

    def __str__(self):
        return f"{self.titre} ({self.categorie} - {self.sous_categorie})"

class Horaire(models.Model):
    JOURS_CHOICES = (
        ('Lundi', 'Lundi'),
        ('Mardi', 'Mardi'),
        ('Mercredi', 'Mercredi'),
        ('Jeudi', 'Jeudi'),
        ('Vendredi', 'Vendredi'),
        ('Samedi', 'Samedi'),
        ('Dimanche', 'Dimanche')
    )
    
    annonce = models.ForeignKey(Annonce, on_delete=models.CASCADE)
    jour = models.CharField(max_length=10, choices=JOURS_CHOICES)
    heure_ouverture = models.TimeField()
    heure_fermeture = models.TimeField()

    class Meta:
        verbose_name = 'Horaire'
        verbose_name_plural = 'Horaires'

    def __str__(self):
        return f"{self.annonce.titre} - {self.jour}"

class Tarif(models.Model):
    annonce = models.ForeignKey(Annonce, on_delete=models.CASCADE, related_name='tarifs')
    nom = models.CharField(max_length=100)
    prix = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Tarif'
        verbose_name_plural = 'Tarifs'

    def __str__(self):
        return f"{self.nom} - {self.prix}€"

class GaleriePhoto(models.Model):
    annonce = models.ForeignKey(Annonce, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='annonces/photos/')
    created = models.DateTimeField(auto_now_add=True, default=timezone.now)

    class Meta:
        verbose_name = 'Photo'
        verbose_name_plural = 'Photos'
        ordering = ['-created']

    def __str__(self):
        return f"Photo pour {self.annonce.titre}"

    def delete(self, *args, **kwargs):
        # Supprimer le fichier physique
        if self.image:
            storage = self.image.storage
            if storage.exists(self.image.name):
                storage.delete(self.image.name)
        # Puis supprimer l'enregistrement de la base de données
        super().delete(*args, **kwargs) 