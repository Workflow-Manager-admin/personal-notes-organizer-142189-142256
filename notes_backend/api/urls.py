from django.urls import path
from .views import (
    health,
    UserRegistrationView,
    UserLoginView,
    UserLogoutView,
    NoteListCreateView,
    NoteRetrieveUpdateDestroyView,
    NoteSearchView,
)

urlpatterns = [
    # Health
    path('health/', health, name='Health'),

    # Auth
    path('auth/register/', UserRegistrationView.as_view(), name='auth-register'),
    path('auth/login/', UserLoginView.as_view(), name='auth-login'),
    path('auth/logout/', UserLogoutView.as_view(), name='auth-logout'),

    # Notes
    path('notes/', NoteListCreateView.as_view(), name='notes-list-create'),
    path('notes/<int:pk>/', NoteRetrieveUpdateDestroyView.as_view(), name='notes-detail'),
    path('notes/search/', NoteSearchView.as_view(), name='notes-search'),
]
