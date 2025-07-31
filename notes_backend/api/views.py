from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth.models import User
from django.db.models import Q

from .models import Note
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    NoteSerializer
)
from rest_framework.permissions import IsAuthenticated, AllowAny

# PUBLIC_INTERFACE
@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    """
    Health check endpoint.

    Returns 200 OK with message if server is running.
    """
    return Response({"message": "Server is up!"})


# PUBLIC_INTERFACE
class UserRegistrationView(APIView):
    """
    Register a new user.

    Create a new user account and obtain an authentication token.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {"token": token.key, "username": user.username},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# PUBLIC_INTERFACE
class UserLoginView(ObtainAuthToken):
    """
    Authenticate an existing user.

    Returns a token to be used for authenticated requests.
    """
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = User.objects.filter(username=serializer.validated_data['username']).first()
            if user and user.check_password(serializer.validated_data['password']):
                token, _ = Token.objects.get_or_create(user=user)
                return Response({"token": token.key, "username": user.username})
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


# PUBLIC_INTERFACE
class UserLogoutView(APIView):
    """
    Log out the user by deleting their API token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request.user.auth_token.delete()
        return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)


# PUBLIC_INTERFACE
class NoteListCreateView(generics.ListCreateAPIView):
    """
    Retrieve all user notes or create a new note.

    GET: List notes belonging to the authenticated user.
    POST: Create a new note for the authenticated user.
    """
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user).order_by('-updated_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# PUBLIC_INTERFACE
class NoteRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific note.
    """
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)


# PUBLIC_INTERFACE
class NoteSearchView(generics.ListAPIView):
    """
    Search notes by keyword in title or content.

    GET params:
        - q: query string to search for (required)

    Returns matching notes for authenticated user.
    """
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        query = self.request.query_params.get('q', '')
        if not query:
            return Note.objects.none()
        return Note.objects.filter(
            user=user
        ).filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        ).order_by('-updated_at')
