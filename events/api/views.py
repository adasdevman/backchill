from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import UserSerializer # type: ignore
from .decorators import verify_token # type: ignore
from ..models import Annonce, Tarif # type: ignore

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.set_password(request.data['password'])
        user.save()
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'token': str(refresh.access_token),
            'user': serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        serializer = UserSerializer(user)
        return Response({
            'token': str(refresh.access_token),
            'user': serializer.data
        })
    return Response({
        'detail': 'Email ou mot de passe incorrect'
    }, status=status.HTTP_401_UNAUTHORIZED) 

@api_view(['GET'])
@verify_token
def user_profile(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['PUT'])
@verify_token
def update_profile(request):
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_tarifs(request, annonce_id):
    try:
        annonce = Annonce.objects.get(id=annonce_id)
        tarifs = Tarif.objects.filter(annonce=annonce)
        data = [{
            'id': t.id,
            'name': t.nom,
            'price': float(t.prix)
        } for t in tarifs]
        return Response(data)
    except Annonce.DoesNotExist:
        return Response({'error': 'Annonce non trouvée'}, status=404) 