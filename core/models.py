from django.db import models

class Payment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('COMPLETED', 'Complété'),
        ('FAILED', 'Échoué'),
    ]

    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    annonce = models.ForeignKey('Annonce', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_type = models.CharField(max_length=20)  # 'ticket' ou 'reservation'
    tarif = models.ForeignKey('Tarif', on_delete=models.SET_NULL, null=True, related_name='payments')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True) 