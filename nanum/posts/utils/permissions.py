from rest_framework import permissions


class IsAuthorOrAuthenticated(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        authenticated = request.user and request.user.is_authenticated
        if request.method in permissions.SAFE_METHODS:
            return authenticated

        # Instance must have an attribute named `owner`.
        return authenticated and obj.user == request.user
