from django.conf.urls import url
from online.order import views

urlpatterns = [
    url(r'^api/orders/$', views.OrderCreateView.as_view()), #创建订单,获取订单列表（翻页）
    url(r'^orders/$', views.OrdersListView.as_view()), #【渲染】获取订单列表

    url(r'^api/orders/(?P<order_no>\d+)/$', views.OrdersDetailView.as_view()),#订单详情

    url(r'^orders/address/$', views.OrderAddressView.as_view()),#【渲染】订单页面（地址）
    url(r'^api/orders/address$', views.UserAddressView.as_view()),  #订单地址保存

    url(r'^orders/(.+)/pay', views.OrderPayView.as_view()),#【渲染】支付页面



]
