from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Read is public; changing/deleting a product is allowed only to its owner or superuser."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user and request.user.is_superuser:
            return True

        return obj.owner_id == request.user.id


class IsReviewAuthorOrReadOnly(permissions.BasePermission):
    """Read is public; changing/deleting a review is allowed only to its author or superuser."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user and request.user.is_superuser:
            return True

        return obj.user_id == request.user.id
