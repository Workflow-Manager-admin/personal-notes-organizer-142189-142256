from django.db import models
from django.contrib.auth import get_user_model

# PUBLIC_INTERFACE
class Note(models.Model):
    """
    A model representing a personal note linked to a user.
    """
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
