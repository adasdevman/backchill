from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserManager(BaseUserManager):
    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('L\'email est obligatoire')
        email = self.normalize_email(email)
        
        # Générer un username à partir de l'email
        username = slugify(email.split('@')[0])
        base_username = username
        counter = 1
        
        # S'assurer que le username est unique
        while self.model.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
            
        # Créer l'utilisateur avec le username généré
        user = self.model(email=email, username=username, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Administrateur'),
        ('ANNONCEUR', 'Annonceur'),
        ('UTILISATEUR', 'Utilisateur')
    )

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='UTILISATEUR')
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    banner_image = models.ImageField(upload_to='banner_images/', null=True, blank=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    taux_avance = models.IntegerField(default=0, help_text='Pourcentage d\'avance requis pour les annonces')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class Preference(models.Model):
    LANGUE_CHOICES = (
        ('FR', 'Français'),
        ('EN', 'Anglais')
    )
    
    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE)
    langue = models.CharField(max_length=2, choices=LANGUE_CHOICES, default='FR')
    notifications = models.BooleanField(default=True)

class Profile(models.Model):
    """
    Modèle de profil utilisateur qui étend le modèle User de Django
    avec des informations supplémentaires, notamment la source d'authentification
    """
    AUTH_SOURCE_CHOICES = [
        ('django', 'Django (email/mot de passe)'),
        ('clerk', 'Clerk (OAuth)'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    auth_source = models.CharField(
        max_length=20, 
        choices=AUTH_SOURCE_CHOICES, 
        default='django',
        help_text="Source d'authentification de l'utilisateur"
    )
    clerk_user_id = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="ID utilisateur Clerk pour les utilisateurs authentifiés via Clerk"
    )
    email_verified = models.BooleanField(
        default=False,
        help_text="Indique si l'email de l'utilisateur a été vérifié"
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Champs pour les préférences de notification
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    
    # Dates importantes pour le suivi
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_source = models.CharField(
        max_length=20, 
        choices=AUTH_SOURCE_CHOICES, 
        blank=True, 
        null=True
    )
    
    def __str__(self):
        return f"{self.user.email} ({self.auth_source})"

    class Meta:
        verbose_name = "Profil Utilisateur"
        verbose_name_plural = "Profils Utilisateurs"

# Signal pour créer automatiquement un profil quand un nouvel utilisateur est créé
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crée un profil pour un nouvel utilisateur"""
    if created:
        Profile.objects.create(
            user=instance,
            auth_source='django',  # Par défaut, on considère que l'utilisateur est créé via Django
            email_verified=False
        )

# Signal pour sauvegarder automatiquement le profil quand l'utilisateur est sauvegardé
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Sauvegarde le profil de l'utilisateur"""
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        # Dans le cas où le profil n'existe pas encore
        Profile.objects.create(
            user=instance,
            auth_source='django',
            email_verified=False
        )
