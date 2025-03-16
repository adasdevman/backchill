# Choix de rôles
ROLE_CHOICES = [
    ('ADMIN', 'Administrateur'),
    ('ANNONCEUR', 'Annonceur'),
    ('UTILISATEUR', 'Utilisateur'),
]

# Messages d'erreur
ERROR_MESSAGES = {
    'not_found': "L'objet demandé n'existe pas",
    'permission_denied': "Vous n'avez pas la permission d'effectuer cette action",
    'validation_error': "Erreur de validation des données",
}

# Configuration
PAGINATION = {
    'default_page_size': 10,
    'max_page_size': 100,
} 