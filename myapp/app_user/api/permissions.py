from rest_framework.permissions import BasePermission


class IsManagerPermission(BasePermission):
    """ Permission for course manager """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.get_manager_permission()
        )