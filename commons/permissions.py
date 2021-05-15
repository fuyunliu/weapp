from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS or
            (hasattr(obj, 'is_owned') and obj.is_owned(request.user))
        )


class IsOwnerOrAdmin(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return user.is_staff or (hasattr(obj, 'is_owned') and obj.is_owned(user))


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
