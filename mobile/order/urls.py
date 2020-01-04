from django.conf.urls import url
from mobile.order import views

urlpatterns = [
    url(r'^api/mobile/orders/$', views.OrdersView.as_view()),  # 创建订单,获取订单列表（翻页）

    url(r'^api/mobile/orders/(?P<order_no>\d+)/$', views.OrdersDetailView.as_view()),  # 获取订单详情

    url(r'^api/mobile/orders/address/$', views.OrderAddressView.as_view()),  # 获取订单信息及地址
    url(r'^api/mobile/orders/(?P<order_no>\d+)/address/$', views.UserAddressView.as_view()),  # 保存订单地址

    url(r'^api/mobile/orders/(?P<order_no>\d+)/pay/$', views.PayOrder.as_view()),  # 支付订单
]
