from django.conf.urls import url
from django.urls import path
from online.order import views

urlpatterns = [
    url(r'^api/orders/$', views.OrderView.as_view()),
    url(r'^orders/$', views.OrdersListView.as_view()),
    url(r'^api/order_detail/$', views.OrdersDetailView.as_view()),
    url(r'^order_address/$', views.OrderAddressView.as_view()),
    path('change_status/', views.OderStatusChange),

]
