from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.exceptions import APIException

class BaseService:
    """
    Service de base avec des méthodes communes
    """
    @staticmethod
    def get_object_or_404(model_class, **kwargs):
        try:
            return model_class.objects.get(**kwargs)
        except ObjectDoesNotExist:
            raise APIException(
                f"{model_class.__name__} non trouvé",
                status.HTTP_404_NOT_FOUND
            )

    @staticmethod
    def validate_data(serializer_class, data):
        serializer = serializer_class(data=data)
        if not serializer.is_valid():
            raise APIException(
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )
        return serializer.validated_data 