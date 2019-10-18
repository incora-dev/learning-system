from django.http.response import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render

from .models import Course


class StudentCourseAccessMixin:
    """
    Check access student for course
    if student doesn't have acess return not allowed template
    """
    def dispatch(self, request, *args, **kwargs):
        course_id = kwargs.get('course_id')
        self.course = get_object_or_404(Course, id=course_id)

        user = request.user
        access = user.course_accesses.filter(course=self.course)
        if not(access.exists() or user.get_manager_permission()):
            return render(request, 'app/not_allowed.html', {})
        return super().dispatch(request, *args, **kwargs)


class ManagerPermission:
    """
    Allow access only for managers
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.get_manager_permission():
            return HttpResponseBadRequest()
        return super().dispatch(request, *args, **kwargs)
