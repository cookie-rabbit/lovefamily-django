from django.conf.urls import url
from management.user import views

urlpatterns = [
    # url(r'^login/',views.LoginView.as_view()),
    url(r'^admin/orders/{order_id}', views.OderStatusChange.as_view()),
]