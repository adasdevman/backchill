from django.db import models
from django.conf import settings
from .base import TimeStampedModel
from .annonce import Annonce, Tarif
from django.core.exceptions import ValidationError
from uuid import uuid4

class Payment(TimeStampedModel):
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('completed', 'Complété'),
        ('failed', 'Échoué'),
        ('refunded', 'Remboursé')
    )

    PAYMENT_TYPE_CHOICES = (
        ('ticket', 'Ticket'),
        ('table', 'Table'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='core_payments'
    )
    annonce = models.ForeignKey(
        Annonce,
        on_delete=models.SET_NULL,
        null=True,
        related_name='payments'
    )
    tarif = models.ForeignKey(
        Tarif,
        on_delete=models.SET_NULL,
        null=True,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True, unique=True)
    description = models.TextField(blank=True)

    # Informations de l'utilisateur au moment du paiement
    user_first_name = models.CharField(max_length=100, default='Non spécifié')
    user_last_name = models.CharField(max_length=100, default='Non spécifié')
    user_email = models.EmailField(default='no-email@example.com')
    user_phone = models.CharField(max_length=20, blank=True)
    user_address = models.CharField(max_length=255, blank=True)
    user_city = models.CharField(max_length=100, blank=True)

    # Informations de l'annonce au moment du paiement
    annonce_titre = models.CharField(max_length=255, default='Non spécifié')
    annonce_categorie = models.CharField(max_length=100, default='Non spécifié')
    annonce_sous_categorie = models.CharField(max_length=100, blank=True)
    annonce_utilisateur_id = models.IntegerField(default=0)  # ID de l'annonceur
    tarif_nom = models.CharField(max_length=100, default='Non spécifié')
    tarif_prix = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize default values for required fields
        if not self.annonce_categorie:
            self.annonce_categorie = 'Non spécifié'
        if not self.annonce_titre:
            self.annonce_titre = 'Non spécifié'
        if not self.tarif_nom:
            self.tarif_nom = 'Non spécifié'
        if not self.user_first_name:
            self.user_first_name = 'Non spécifié'
        if not self.user_last_name:
            self.user_last_name = 'Non spécifié'
        if not self.user_email:
            self.user_email = 'no-email@example.com'

    def clean(self):
        # Vérifier que le montant est positif
        if self.amount <= 0:
            raise ValidationError({'amount': 'Le montant doit être supérieur à 0'})
            
        # Vérifier que l'annonce est renseignée
        if not self.annonce:
            raise ValidationError({'annonce': 'L\'annonce est requise'})
            
        # Vérifier que le tarif est renseigné
        if not self.tarif:
            raise ValidationError({'tarif': 'Le tarif est requis'})
            
        # Vérifier que le tarif appartient bien à l'annonce
        if self.tarif and self.annonce and self.tarif.annonce != self.annonce:
            raise ValidationError({'tarif': 'Le tarif sélectionné n\'appartient pas à cette annonce'})

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            # Générer un ID de transaction unique
            self.transaction_id = f"TR-{str(uuid4())[:8]}"

        # Ensure we have the related objects loaded before accessing their attributes
        if self.annonce_id and not hasattr(self.annonce, 'titre'):
            try:
                self.annonce = Annonce.objects.select_related('categorie', 'sous_categorie').get(id=self.annonce_id)
            except Annonce.DoesNotExist:
                pass

        if self.tarif_id and not hasattr(self.tarif, 'nom'):
            try:
                self.tarif = Tarif.objects.get(id=self.tarif_id)
            except Tarif.DoesNotExist:
                pass

        # Sauvegarder les informations de l'utilisateur
        if self.user:
            self.user_first_name = self.user.first_name or 'Non spécifié'
            self.user_last_name = self.user.last_name or 'Non spécifié'
            self.user_email = self.user.email or 'no-email@example.com'
            self.user_phone = getattr(self.user, 'phone_number', '') or ''
            self.user_address = getattr(self.user, 'address', '') or ''
            self.user_city = getattr(self.user, 'city', '') or ''

        # Sauvegarder les informations de l'annonce
        if self.annonce:
            try:
                self.annonce_titre = self.annonce.titre or 'Non spécifié'
                self.annonce_categorie = (self.annonce.categorie.nom if hasattr(self.annonce, 'categorie') and self.annonce.categorie else 'Non spécifié')
                self.annonce_sous_categorie = (self.annonce.sous_categorie.nom if hasattr(self.annonce, 'sous_categorie') and self.annonce.sous_categorie else '')
                self.annonce_utilisateur_id = self.annonce.utilisateur_id or 0
            except Exception as e:
                print(f"Error getting announcement details: {e}")

        # Sauvegarder les informations du tarif
        if self.tarif:
            try:
                self.tarif_nom = self.tarif.nom or 'Non spécifié'
                self.tarif_prix = self.tarif.prix or 0
            except Exception as e:
                print(f"Error getting tarif details: {e}")

        # Final safety check - ensure no null values
        self.annonce_titre = self.annonce_titre or 'Non spécifié'
        self.annonce_categorie = self.annonce_categorie or 'Non spécifié'
        self.annonce_sous_categorie = self.annonce_sous_categorie or ''
        self.annonce_utilisateur_id = self.annonce_utilisateur_id or 0
        self.tarif_nom = self.tarif_nom or 'Non spécifié'
        self.tarif_prix = self.tarif_prix or 0
        self.user_first_name = self.user_first_name or 'Non spécifié'
        self.user_last_name = self.user_last_name or 'Non spécifié'
        self.user_email = self.user_email or 'no-email@example.com'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Paiement #{self.transaction_id} - {self.amount} FCFA par {self.user_email} ({self.status})" 