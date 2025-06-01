"""
Module intermédiaire pour résoudre les importations entre urls.py et views.py
Ce fichier évite les importations circulaires en important explicitement depuis views.py
"""

try:
    # Importation directe depuis le fichier principal views.py (chemin absolu)
    from api.views import (
        login_view, register_view, register_annonceur_view,
        profile_view, CategorieList, AnnonceList, AnnonceDetail,
        create_payment, payment_history, CinetPayWebhookView,
        check_email, mes_annonces, mes_tickets, mes_chills,
        NotificationViewSet, upload_annonce_photo, received_bookings,
        sold_tickets, delete_account_view, FacebookDataDeletionView,
        UploadAnnonceVideoView
    )
except ImportError:
    # Chemin alternatif (au cas où views.py est dans un autre répertoire)
    import sys
    import os
    import inspect
    import logging
    
    logger = logging.getLogger(__name__)
    logger.warning("Tentative d'importation alternative pour les vues")
    
    # Chemin courant du fichier
    current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parent_dir = os.path.dirname(current_dir)
    
    # Ajout du répertoire parent au PATH pour permettre l'importation
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    try:
        # Importation directe depuis le chemin du fichier
        from views import (
            login_view, register_view, register_annonceur_view,
            profile_view, CategorieList, AnnonceList, AnnonceDetail,
            create_payment, payment_history, CinetPayWebhookView,
            check_email, mes_annonces, mes_tickets, mes_chills,
            NotificationViewSet, upload_annonce_photo, received_bookings,
            sold_tickets, delete_account_view, FacebookDataDeletionView,
            UploadAnnonceVideoView
        )
        logger.info("Importation alternative des vues réussie")
    except ImportError as e:
        logger.error(f"Échec de l'importation des vues: {str(e)}")
        # Définir des vues factices pour éviter les erreurs d'importation
        # Cela permettra au moins de charger l'application et d'afficher une erreur plus propre
        from rest_framework.response import Response
        from rest_framework import status
        from rest_framework.decorators import api_view
        
        @api_view(['GET', 'POST'])
        def login_view(request):
            return Response({"error": "Vue non disponible - problème d'importation"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        @api_view(['GET', 'POST'])
        def register_view(request):
            return Response({"error": "Vue non disponible - problème d'importation"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        @api_view(['GET', 'POST'])
        def register_annonceur_view(request):
            return Response({"error": "Vue non disponible - problème d'importation"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        @api_view(['GET', 'POST'])
        def profile_view(request):
            return Response({"error": "Vue non disponible - problème d'importation"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Définir des classes factices pour les autres vues
        class CategorieList:
            @classmethod
            def as_view(cls):
                def view(request):
                    return Response({"error": "Vue non disponible - problème d'importation"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                return view
        
        class AnnonceList:
            @classmethod
            def as_view(cls):
                def view(request):
                    return Response({"error": "Vue non disponible - problème d'importation"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                return view
        
        class AnnonceDetail:
            @classmethod
            def as_view(cls):
                def view(request, pk):
                    return Response({"error": "Vue non disponible - problème d'importation"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                return view
        
        class CinetPayWebhookView:
            @classmethod
            def as_view(cls):
                def view(request):
                    return Response({"error": "Vue non disponible - problème d'importation"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                return view
        
        class FacebookDataDeletionView:
            @classmethod
            def as_view(cls):
                def view(request):
                    return Response({"error": "Vue non disponible - problème d'importation"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                return view
        
        class UploadAnnonceVideoView:
            @classmethod
            def as_view(cls):
                def view(request):
                    return Response({"error": "Vue non disponible - problème d'importation"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                return view
        
        class NotificationViewSet:
            pass
        
        create_payment = login_view
        payment_history = login_view
        check_email = login_view
        mes_annonces = login_view
        mes_tickets = login_view
        mes_chills = login_view
        upload_annonce_photo = login_view
        received_bookings = login_view
        sold_tickets = login_view
        delete_account_view = login_view
