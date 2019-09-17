from rest_framework.permissions import BasePermission


class HasCoursePermission(BasePermission):
    """ Permission for course manager """

    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        access = request.user.course_accesses.filter(course=obj)

        return access.exists() or request.user.get_manager_permission()