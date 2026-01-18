from django.db.models import Q
from rest_framework import viewsets
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from blog.models import Post
from blog.serializers import PostSerializer, UserSerializer
from blog.permissions import IsAuthorOrReadOnly


@api_view(["GET"])
def api_root(request):
    return Response(
        {
            "users": reverse("user-list", request=request),
            "posts": reverse("post-list", request=request),
        }
    )


class UserReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,
    ]

    def get_queryset(self):
        """
        Returns published posts for all users,
        and includes unpublished posts owned by the current user.
        """
        user = self.request.user

        if user.is_authenticated:
            return Post.objects.filter(
                Q(is_published=True) | Q(author=user)
            )

        return Post.objects.filter(is_published=True)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
