from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User
from .serializers import UserSerializer, UserCreateSerializer
from .permissions import IsAdmin


class RoleTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = getattr(user, 'role', None)
        return token

    def validate(self, attrs):
        # Add debug logging
        print(f"Login attempt with attrs: {attrs}")
        try:
            data = super().validate(attrs)
            data['role'] = getattr(self.user, 'role', None)
            print(f"Login successful for user: {self.user.username}")
            return data
        except Exception as e:
            print(f"Login failed with error: {e}")
            raise


class RoleTokenObtainPairView(TokenObtainPairView):
    serializer_class = RoleTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def ban(self, request, pk=None):
        """Ban a user (set is_active to False)"""
        user = self.get_object()
        
        # Prevent banning admins
        if user.role == 'ADMIN':
            return Response(
                {'detail': 'Cannot ban admin users.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Prevent self-ban
        if user.id == request.user.id:
            return Response(
                {'detail': 'Cannot ban yourself.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user.is_active = False
        user.save()
        return Response({'detail': f'User {user.username} has been banned.'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def unban(self, request, pk=None):
        """Unban a user (set is_active to True)"""
        user = self.get_object()
        
        user.is_active = True
        user.save()
        return Response({'detail': f'User {user.username} has been unbanned.'})
    
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
from django.shortcuts import render

# Create your views here.
