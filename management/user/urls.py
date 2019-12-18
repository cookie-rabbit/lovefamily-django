from django.conf.urls import url

from management.user import views

urlpatterns = [
    url(r'^login/',views.LoginView.as_view()),
    url(r'^users/',views.UsersView.as_view())
]