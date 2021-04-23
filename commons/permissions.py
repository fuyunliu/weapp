from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS or
            obj.author == request.user
        )


class IsMeOrAdmin(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return (
            user.is_staff or
            (type(obj) == type(user) and obj.pk == user.pk)
        )


class IsMeOrAdminOrReadOnly(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return (
            request.method in permissions.SAFE_METHODS or
            user.is_staff or
            (type(obj) == type(user) and obj.pk == user.pk)
        )
