from django.conf.urls import url

from online.account import views

urlpatterns = [
    url(r'^api/account/login/$', views.LoginView.as_view()),
    url(r'^account/$',views.UserView.as_view()),
    url(r'^api/account/$',views.UserView.as_view()),
    url(r'^api/account/logout/$',views.LogoutView.as_view()),
    url(r'^api/account/signup/$',views.SignUpView.as_view()),
    url(r'^account/signup/$',views.SignUpTemplateView.as_view())
]