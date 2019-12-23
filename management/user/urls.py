from django.conf.urls import url

from management.user import views

urlpatterns = [
    url(r'^login/$',views.LoginView.as_view()),
    url(r'^api/users/$',views.UsersView.as_view()),
    url(r'^user/(?P<user_id>\d+)/$',views.UserView.as_view())
]