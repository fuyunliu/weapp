from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        owner = getattr(obj, 'author', None) or getattr(obj, 'sender', None)
        return (
            request.method in permissions.SAFE_METHODS or
            owner == request.user
        )


class IsOwnerOrAdmin(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        user = request.user
        owner = getattr(obj, 'user', None)
        return user.is_staff or owner == user


class IsMeOrAdmin(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return user.is_staff or obj == user


class IsMeOrAdminOrReadOnly(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return (
            request.method in permissions.SAFE_METHODS or
            user.is_staff or obj == user
        )
