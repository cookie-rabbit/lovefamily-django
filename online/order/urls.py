from django.conf.urls import url
from online.order import views

urlpatterns = [
    url(r'^api/orders/$', views.OrderCreateView.as_view()),
    url(r'^orders/$', views.OrdersListView.as_view()),

    url(r'^api/orders/more/$', views.OrdersOffsetView.as_view()),
    url(r'^api/order_detail/$', views.OrdersDetailView.as_view()),

    url(r'^orders/address/$', views.OrderAddressView.as_view()),
    url(r'^api/orders/address$', views.UserAddressView.as_view()),

    url(r'^orders/(.+)/pay', views.OrderPayView.as_view()),

    url(r'^admin/orders/{order_id}', views.OderStatusChange),

]
