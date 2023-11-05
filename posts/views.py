from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response


from posts.serializers import (
    PostListSerializer,
    PostRetrieveSerializer,
    PostSerializer,
)

from .models import Post


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action in ("list", "home"):
            return PostListSerializer

        if self.action == "retrieve":
            return PostRetrieveSerializer

        return PostSerializer

    @action(
        methods=["GET"],
        detail=False,
        url_path="home",
        permission_classes=[AllowAny],
    )
    def home(self, request):
        """Retrieve posts created by the current user
        or the users they are following"""
        posts = self.get_queryset().filter(
            Q(user=request.user)
            | Q(user__profile__followers=request.user.profile)
        )
        serializer = self.get_serializer(posts, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["POST"],
        detail=True,
        url_path="like",
        permission_classes=[IsAuthenticated],
    )
    def like(self, request, pk=None):
        """Like/unlike a post"""
        user = request.user
        post = self.get_object()

        if user in post.likes.all():
            post.likes.remove(user)
            return Response(
                {"status": "Unliked the post"}, status=status.HTTP_200_OK
            )
        post.likes.add(user)
        return Response(
            {"status": "Liked the post"}, status=status.HTTP_200_OK
        )

    @action(
        methods=["GET"],
        detail=False,
        url_path="liked",
        permission_classes=[AllowAny],
    )
    def liked(self, request):
        """Retrieve liked posts"""
        posts = self.get_queryset().filter(likes__id=request.user.id)
        serializer = self.get_serializer(posts, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
