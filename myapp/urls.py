"""myapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from rest_framework_swagger.views import get_swagger_view

from myapp.app_core.views import CourseListView, index
from myapp.app_core.ckeditor_uploader import upload


schema_view = get_swagger_view(title='myapp API')

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^$', index, name='index'),
    url(r'^library', login_required(CourseListView.as_view()), name='home'),
    url(r'^course/', include('myapp.app_core.urls')),
    url(r'', include('myapp.app_user.urls')),

    url(r'^ckeditor/upload/$', staff_member_required(upload), name='ckeditor_upload'),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),

    url(r'^api/docs/$', schema_view, name='api_docs'),
    url(r'^api/accounts/', include('myapp.app_user.api.urls', namespace='api_accounts')),
    url(r'^api/core/', include('myapp.app_core.api.urls', namespace='api_core')),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)\
 + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
