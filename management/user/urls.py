from django.conf.urls import url

from management.user import views

urlpatterns = [
    url(r'^api/admin/login/$',views.LoginView.as_view()),
    url(r'^api/admin/users/$',views.UsersView.as_view()),
    url(r'^api/admin/user/(?P<user_id>\d+)/$',views.UserView.as_view())
]