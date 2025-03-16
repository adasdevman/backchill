from django.db import models

class TimeStampedModel(models.Model):
    """
    Un modèle abstrait qui ajoute des champs created et modified
    """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True 