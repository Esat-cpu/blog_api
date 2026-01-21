from rest_framework import serializers
from django.contrib.auth.models import User
from blog.models import Post


class PostSerializer(serializers.HyperlinkedModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    slug = serializers.ReadOnlyField()

    class Meta:
        model = Post
        fields = [
            "url",
            "id",
            "title",
            "slug",
            "content",
            "author",
            "is_published",
            "created_at",
        ]


class UserSerializer(serializers.HyperlinkedModelSerializer):
    posts = serializers.HyperlinkedRelatedField(
        many=True, view_name="post-detail", read_only=True
    )

    class Meta:
        model = User
        fields = ["url", "id", "username", "posts"]
