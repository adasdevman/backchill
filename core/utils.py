import os
from uuid import uuid4
from django.utils.text import slugify

def get_file_path(instance, filename):
    """
    Génère un chemin de fichier unique pour les uploads
    """
    ext = filename.split('.')[-1]
    filename = f"{uuid4().hex}.{ext}"
    return os.path.join('uploads', filename)

def generate_unique_slug(model_instance, slugable_field_name, slug_field_name):
    """
    Génère un slug unique pour un modèle
    """
    slug = slugify(getattr(model_instance, slugable_field_name))
    unique_slug = slug
    extension = 1

    model_class = model_instance.__class__
    while model_class.objects.filter(
        **{slug_field_name: unique_slug}
    ).exists():
        unique_slug = f"{slug}-{extension}"
        extension += 1
    
    return unique_slug 