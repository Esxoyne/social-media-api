from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
)

from .models import Post
from .permissions import IsAuthor
from .tasks import defer_post
from .serializers import (
    PostCreateSerializer,
    PostListSerializer,
    PostRetrieveSerializer,
    PostSerializer,
)
from core.pagination import StandardResultSetPagination
from core.serializers import EmptySerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(published=True)
    serializer_class = PostSerializer
    permission_classes = (AllowAny,)
    pagination_class = StandardResultSetPagination
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

        if self.action in ("list", "retrieve", "home"):
            queryset = queryset.select_related(
                "user__profile"
            ).prefetch_related("images", "tags", "likes")

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action in ("list", "home", "liked", "replies"):
            return PostListSerializer

        if self.action == "retrieve":
            return PostRetrieveSerializer

        if self.action == "like":
            return EmptySerializer

        if self.action in ("create", "add_reply"):
            return PostCreateSerializer

        return PostSerializer

    def get_permissions(self):
        if self.action in (
            "create",
            "home",
            "like",
            "unlike",
            "liked",
            "add_reply",
        ):
            return (IsAuthenticated(),)

        if self.action in ("update", "partial_update", "destroy"):
            return (IsAuthor(),)

        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        publish_at = serializer.validated_data.pop("publish_at", None)
        if publish_at and publish_at > timezone.now():
            post = self.perform_create(serializer, published=False)
            defer_post.apply_async((post.id,), eta=publish_at)
        else:
            self.perform_create(serializer)

        data = serializer.data
        data["publish_at"] = publish_at

        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    @action(
        methods=["GET"],
        detail=False,
        url_path="home",
        permission_classes=[AllowAny],
    )
    def home(self, request) -> Response:
        """
        Retrieve posts created by the current user
        or the users they are following
        """
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
        """
        Like a post
        """
        user = request.user
        post = self.get_object()

        if user not in post.likes.all():
            post.likes.add(user)
            return Response(
                {}, status=status.HTTP_200_OK
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @like.mapping.delete
    def unlike(self, request, pk=None) -> Response:
        """
        Unlike a post
        """
        user = request.user
        post = self.get_object()

        if user in post.likes.all():
            post.likes.remove(user)
            return Response(
                {}, status=status.HTTP_200_OK
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=["GET"],
        detail=False,
        url_path="liked",
        permission_classes=[AllowAny],
    )
    def liked(self, request) -> Response:
        """
        Retrieve posts liked by the current user
        """
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
        """
        Retrieve replies
        """
        parent = self.get_object()
        replies = self.get_queryset().filter(parent=parent)
        serializer = self.get_serializer(replies, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @replies.mapping.post
    def add_reply(self, request, pk=None) -> Response:
        """
        Add a reply
        """
        parent = self.get_object()
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        publish_at = serializer.validated_data.pop("publish_at", None)
        if publish_at:
            post = self.perform_create(
                serializer,
                published=False,
                parent=parent,
            )
            defer_post.apply_async((post.id,), eta=publish_at)
        else:
            self.perform_create(serializer, parent=parent)

        data = serializer.data
        data["publish_at"] = publish_at

        return Response(data, status=status.HTTP_200_OK)

    def perform_create(self, serializer, **kwargs):
        return serializer.save(user=self.request.user, **kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "search",
                type=str,
                description="Search by text",
            ),
            OpenApiParameter(
                "tags",
                type={"type": "list", "items": {"type": "string"}},
                description="Filter by tags",
            ),
            OpenApiParameter(
                "user",
                type=int,
                description="Filter by user id"
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        List all posts
        """
        return super().list(request, *args, **kwargs)
