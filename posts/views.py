from django.db.models import Q
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend


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
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ("user",)
    search_fields = ("text",)

    def get_queryset(self):
        queryset = self.queryset

        tags = self.request.query_params.get("tags")

        if tags:
            tags = tags.split(",")
            for tag in tags:
                queryset = queryset.filter(tags__name__in=[tag])

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action in ("list", "home", "liked", "replies"):
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
    def home(self, request) -> Response:
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
    def like(self, request, pk=None) -> Response:
        """Like a post"""
        user = request.user
        post = self.get_object()

        if user not in post.likes.all():
            post.likes.add(user)
            return Response(
                {"status": "Liked the post"}, status=status.HTTP_200_OK
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @like.mapping.delete
    def unlike(self, request, pk=None) -> Response:
        """Unlike a post"""
        user = request.user
        post = self.get_object()

        if user in post.likes.all():
            post.likes.remove(user)
            return Response(
                {"status": "Unliked the post"}, status=status.HTTP_200_OK
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=["GET"],
        detail=False,
        url_path="liked",
        permission_classes=[AllowAny],
    )
    def liked(self, request) -> Response:
        """Retrieve liked posts"""
        posts = self.get_queryset().filter(likes__id=request.user.id)
        serializer = self.get_serializer(posts, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=True,
        url_path="replies",
        permission_classes=[AllowAny],
    )
    def replies(self, request, pk=None) -> Response:
        """Retrieve replies"""
        parent = self.get_object()
        replies = self.get_queryset().filter(parent=parent)
        serializer = self.get_serializer(replies, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @replies.mapping.post
    def add_reply(self, request, pk=None) -> Response:
        """Add a reply"""
        parent = self.get_object()
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer, parent=parent)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer, **kwargs):
        serializer.save(user=self.request.user, **kwargs)
