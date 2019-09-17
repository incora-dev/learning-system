from django.conf.urls import url
from django.contrib.auth import views
from mylearnview.mylearnview_user.forms import LoginForm


urlpatterns = [
    url(r'^login/$', views.LoginView.as_view(form_class = LoginForm), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(template_name='registration/logout.html'), name='logout'),
]