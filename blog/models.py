import uuid
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User

class Post(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=75, unique=True)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def save(self, *args, **kwargs):
        """
        Create a unique slug.
        """
        if not self.slug:
            base = slugify(self.title) or "post"
            self.slug = f"{base[:65]}-{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)
