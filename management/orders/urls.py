from django.conf.urls import url
from management.orders import views

urlpatterns = [
    # url(r'^login/',views.LoginView.as_view()),
    url(r'^api/admin/orders/status/$', views.OderStatusChange.as_view()),
    url(r'^api/admin/orders/$', views.OrdersView.as_view()),
    url(r'^api/admin/orders/detail/$', views.OrderDetailView.as_view()),
    url(r'^api/admin/orders/status/log/$', views.OrderStatusView.as_view()),
]
