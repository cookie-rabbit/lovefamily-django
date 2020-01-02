from django.conf.urls import url

from online.account import views

urlpatterns = [
    url(r'^api/mobile/accounts/$', views.LoginView.as_view()),  # 用户登录,注册
    url(r'^api/mobile/users/$', views.UserView.as_view()),  # 获取/修改用户信息，地址
    url(r'^api/account/logout/$', views.LogoutView.as_view()),  # 用户退出登录（手机端暂未使用）
]
