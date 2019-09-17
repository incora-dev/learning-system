from django.utils import timezone
from django.db.models import Prefetch, Subquery, OuterRef

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, \
    CreateAPIView, get_object_or_404
from rest_framework.views import Response
from rest_framework.permissions import IsAuthenticated

from mylearnview.mylearnview_core.models import Course, StudentPageNote, StudentPageHistory, Module
from mylearnview.mylearnview_user.api.mixins import ManagerPermissionCreateUpdate

from .serializers import CourseSerializer, CourseDetailSerializer, ModuleDetailSerializer, \
    PageCreateSerializer, PageDetailSerializer, PageNoteSerializer
from .permissions import HasCoursePermission


class CourseListCreateAPIView(ManagerPermissionCreateUpdate, ListCreateAPIView):
    """
    Endpoint for get courses list or create course
    """
    serializer_class = CourseSerializer

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer
        if self.request.user.get_manager_permission():
            data = {'access': serializer(Course.objects.all().order_by('-created_datetime'), many=True).data, 'closed': []}
        else:
            access = Course.objects.filter(student_acesses__student__id__contains=self.request.user.pk).order_by('-created_datetime')
            closed = Course.objects.exclude(student_acesses__student__id__contains=self.request.user.pk).order_by('-created_datetime')
            data = {'access': serializer(access, many=True).data, 'closed': serializer(closed, many=True).data}
        
        return Response(data)

    def perform_create(self, serializer):
        serializer.save(created_by_id=self.request.user.pk)


class CourseRetrieveUpdateAPIView(ManagerPermissionCreateUpdate, RetrieveUpdateDestroyAPIView, CreateAPIView):

    lookup_url_kwarg = 'course_pk'
    permission_classes = [IsAuthenticated, HasCoursePermission]

    def get_queryset(self):
        pagehistory_query = StudentPageHistory.objects.filter(student=self.request.user, module_id=OuterRef('id')).\
            order_by('-last_visited_datetime').values('last_page__sort_index')

        modules_query = Module.objects.annotate(last_opened=Subquery(pagehistory_query[:1]))

        queryset = Course.objects.prefetch_related(
            Prefetch('modules', modules_query)
        )

        return queryset

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CourseDetailSerializer
        elif self.request.method == 'POST':
            return ModuleDetailSerializer
        return CourseSerializer

    def perform_create(self, serializer):
        serializer.save(course_id=self.get_object().id, created_by_id=self.request.user.id)


class CourseModuleRetriveUpdateAPIView(ManagerPermissionCreateUpdate, RetrieveUpdateDestroyAPIView, CreateAPIView):

    lookup_url_kwarg = 'module_pk'
    serializer_class = ModuleDetailSerializer

    def get_queryset(self):
        course_pk = self.kwargs.get('course_pk')

        pagehistory_query = StudentPageHistory.objects.filter(student=self.request.user, module_id=OuterRef('id')). \
            order_by('-last_visited_datetime').values('last_page__sort_index')

        modules_query = Module.objects.annotate(last_opened=Subquery(pagehistory_query[:1]))

        course_queryset = Course.objects.prefetch_related(
            Prefetch('modules', modules_query)
        )

        course = get_object_or_404(course_queryset, pk=course_pk)
        permission = HasCoursePermission()
        if not permission.has_object_permission(self.request, self, course):
            self.permission_denied(
                self.request, message=getattr(permission, 'message', None)
            )

        qs = course.modules.prefetch_related('pages')
        return qs

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PageCreateSerializer
        return ModuleDetailSerializer

    def perform_create(self, serializer):
        module = self.get_object()
        serializer.save(module=module, sort_index=module.pages.count()+1)


class ModulePageRetriveUpdateAPIVeiw(ManagerPermissionCreateUpdate, RetrieveUpdateDestroyAPIView, CreateAPIView):

    lookup_field = 'sort_index'
    lookup_url_kwarg = 'page_num'

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PageNoteSerializer
        if self.request.method == 'GET':
            self.save_history(self.module, self.get_object())
        return PageDetailSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        course_pk = self.kwargs.get('course_pk')
        module_pk = self.kwargs.get('module_pk')

        course = get_object_or_404(Course, pk=course_pk)
        permission = HasCoursePermission()
        if not permission.has_object_permission(self.request, self, course):
            self.permission_denied(
                self.request, message=getattr(permission, 'message', None)
            )

        self.module = get_object_or_404(course.modules.prefetch_related('pages').all(), pk=module_pk)
        return self.module.pages.order_by('sort_index')

    def save_history(self, cur_module, page):
        cur_user = self.request.user
        page_history = StudentPageHistory.objects.filter(student=cur_user, module=cur_module, last_page=page)
        if page_history:
            page_history.last_visited_datetime = timezone.now()
        cur_history = StudentPageHistory(
            student=cur_user,
            module=cur_module,
            last_page=page
        )
        print(cur_history)
        cur_history.save()
        return True

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        notes_serializer = PageNoteSerializer(instance.notes.filter(student=self.request.user), many=True)
        data = {}
        data.update(serializer.data)
        data.update({'notes': notes_serializer.data})
        return Response(data)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user, page=self.get_object())


class PageNoteRetriveUpdateAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = PageNoteSerializer
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        qs = StudentPageNote.objects.filter(student=self.request.user).select_related('page__module__course')
        return qs

    def get_object(self):
        note = super().get_object()
        course = note.page.module.course
        permission = HasCoursePermission()
        if not permission.has_object_permission(self.request, self, course):
            self.permission_denied(
                self.request, message=getattr(permission, 'message', None)
            )
        return note