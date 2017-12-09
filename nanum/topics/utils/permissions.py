from rest_framework import permissions


class IsStaffOrAuthenticatedReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):

        # request.method 가 SAFE_METHOD일 경우(GET, OPTION, HEAD), 유저가 authenticate만 되어 있으면 return
        authenticated = request.user and request.user.is_authenticated
        if request.method in permissions.SAFE_METHODS:
            return authenticated

        # request.method 가 PATCH, PUT, DESTROY 등 변경사항이 필요한 경우 staff user
        return request.user and request.user.is_staff
