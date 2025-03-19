from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from users.models import User
from ..serializers.auth import RegisterSerializer
from django.template.loader import render_to_string

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Générer le token d'activation
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Construire l'URL d'activation
        activation_url = f"chillnow://activate/{uid}/{token}"
        
        # Envoyer l'email d'activation
        context = {
            'user': user,
            'activation_url': activation_url
        }
        email_body = render_to_string('activation_email.html', context)
        
        send_mail(
            'Activez votre compte Chillnow',
            email_body,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=email_body
        )
        
        return Response({
            'message': 'Un email d\'activation a été envoyé à votre adresse email.'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        
        # Envoyer l'email de bienvenue
        context = {
            'user': user
        }
        welcome_email = render_to_string('welcome_email.html', context)
        
        send_mail(
            'Bienvenue sur Chillnow !',
            welcome_email,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=welcome_email
        )
        
        return Response({
            'message': 'Votre compte a été activé avec succès !'
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'message': 'Le lien d\'activation est invalide.'
        }, status=status.HTTP_400_BAD_REQUEST) 