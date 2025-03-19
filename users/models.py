from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.text import slugify

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
