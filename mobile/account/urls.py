from django.conf.urls import url

from online.account import views

urlpatterns = [
    url(r'^api/phone/account/$', views.LoginView.as_view()),#用户登录,注册
    url(r'^api/phone/user/$',views.UserView.as_view()),
    url(r'^address/$',views.MyAddressView.as_view()),
    url(r'^api/address/$',views.MyAddressView.as_view()),
    url(r'^api/account/logout/$',views.LogoutView.as_view()),
    url(r'^api/account/signup/$',views.SignUpView.as_view()),
    url(r'^account/signup/$',views.SignUpTemplateView.as_view())
]