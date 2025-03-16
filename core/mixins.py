from rest_framework.response import Response
from rest_framework import status

class ServiceExceptionHandlerMixin:
    """
    Mixin pour gérer les exceptions dans les services
    """
    def handle_exception(self, exc):
        if hasattr(exc, 'detail'):
            return Response(
                {'error': str(exc.detail)},
                status=exc.status_code
            )
        return Response(
            {'error': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class ValidatorMixin:
    """
    Mixin pour la validation des données
    """
    @classmethod
    def validate_required_fields(cls, data, required_fields):
        missing_fields = [
            field for field in required_fields 
            if not data.get(field)
        ]
        if missing_fields:
            raise ValueError(
                f"Champs requis manquants : {', '.join(missing_fields)}"
            ) 