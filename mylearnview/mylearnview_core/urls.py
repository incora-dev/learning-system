from django.conf.urls import url
from mylearnview.mylearnview_core.views import (
    ModuleListView, ModuleDetailView, ModuleCreateView, CourseCreateView, ImagePageCreateView, CustomPageCreateView,
    ModuleOverviewView, PageUpdateView, ModuleUpdateView, ModuleDeleteView, CourseUpdateView, CourseDeleteView,
    PageDeleteView, StudentPageNoteUpdateView, StudentPageNoteDeleteView
)
from django.contrib.auth.decorators import login_required


urlpatterns = [
    url(r'^add/$', login_required(CourseCreateView.as_view()), name='course_add'),
    url(r'^(?P<pk>\d+)/edit/$', login_required(CourseUpdateView.as_view()),
        name='course_edit'),
    url(r'^(?P<pk>\d+)/delete/$', login_required(CourseDeleteView.as_view()),
        name='course_delete'),
    url(r'^(?P<course_id>\d+)/$', login_required(ModuleListView.as_view()),
        name='course_detail'),
    url(r'^(?P<course_id>\d+)/module/add/$', login_required(ModuleCreateView.as_view()),
        name='module_add'),
    url(r'^(?P<course_id>\d+)/module/(?P<module_id>\d+)/study/$', login_required(ModuleDetailView.as_view()),
        name='module_detail'),
    url(r'^(?P<course_id>\d+)/module/(?P<pk>\d+)/edit/$', login_required(ModuleUpdateView.as_view()),
        name='module_edit'),
    url(r'^(?P<course_id>\d+)/module/(?P<pk>\d+)/delete/$', login_required(ModuleDeleteView.as_view()),
        name='module_delete'),
    url(r'^(?P<course_id>\d+)/module/(?P<module_id>\d+)/overview/$', login_required(ModuleOverviewView.as_view()),
        name='module_overview'),
    url(r'^(?P<course_id>\d+)/module/(?P<module_id>\d+)/page/(?P<pk>\d+)/edit/$',
        login_required(PageUpdateView.as_view()), name='page_edit'),
    url(r'^(?P<course_id>\d+)/module/(?P<module_id>\d+)/page/(?P<pk>\d+)/delete/$',
        login_required(PageDeleteView.as_view()), name='page_delete'),
    url(r'^(?P<course_id>\d+)/module/(?P<pk>\d+)/imgpage/add/$', login_required(ImagePageCreateView.as_view()),
        name='img_page_add'),
    url(r'^(?P<course_id>\d+)/module/(?P<module_id>\d+)/cstmpage/add/$', login_required(CustomPageCreateView.as_view()),
        name='custom_page_add'),
    url(r'^(?P<course_id>\d+)/module/(?P<module_id>\d+)/note/(?P<note_id>\d+)/edit/$',
        login_required(StudentPageNoteUpdateView.as_view()), name='student_page_note_edit'),
    url(r'^(?P<course_id>\d+)/module/(?P<module_id>\d+)/note/(?P<note_id>\d+)/delete/$',
        login_required(StudentPageNoteDeleteView.as_view()), name='student_page_note_delete'),
]