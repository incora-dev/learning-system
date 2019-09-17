from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^courses/$', views.CourseListCreateAPIView.as_view(), name='courses'),
    url(r'^courses/(?P<course_pk>[0-9]+)/$', views.CourseRetrieveUpdateAPIView.as_view(), name='course_detail'),
    url(r'^courses/(?P<course_pk>[0-9]+)/module/(?P<module_pk>[0-9]+)/$', views.CourseModuleRetriveUpdateAPIView.as_view(), name='course_detail'),
    url(r'^courses/(?P<course_pk>[0-9]+)/module/(?P<module_pk>[0-9]+)/(?P<page_num>[0-9]+)/$', views.ModulePageRetriveUpdateAPIVeiw.as_view(), name='module_page'),
    url(r'^notes/(?P<pk>[0-9]+)/$', views.PageNoteRetriveUpdateAPIView.as_view(), name='page_note')
]