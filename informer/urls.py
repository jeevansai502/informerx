from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from informer import views
from informer import healthz
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^health', healthz.health),
    url(r'^$',views.IndexPageView.as_view()),        
    url(r'^logout/$',views.LogoutPageView.as_view()),
    url(r'^login/$',views.LoginPageView.as_view()),
    url(r'^register/$',views.RegisterPageView.as_view()),
    url(r'^dashboard/$',views.MainPageView.as_view()),
    url(r'^email/$',views.EmailPageView.as_view()),
    url(r'^message/$',views.MsgPageView.as_view()),
    url(r'^call/$',views.CallPageView.as_view()),
    #url(r'^users/$',views.UsersPageView.as_view()),
    url(r'emaildata/$',views.EmailData.as_view()),
    url(r'msgdata/$',views.MsgData.as_view()),
    url(r'calldata/$',views.MsgData.as_view()),
    url(r'^emailload/$',views.EmailLoad.as_view()),
    url(r'^msgload/$',views.MsgLoad.as_view()),
    url(r'^callload/$',views.CallLoad.as_view()),
]
