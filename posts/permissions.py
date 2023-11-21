from rest_framework import permissions


class IsAuthor(permissions.BasePermission):
    """
    Check that the authenticated user is the author of the post
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
