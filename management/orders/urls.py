from django.conf.urls import url
from management.orders import views

urlpatterns = [
    # url(r'^login/',views.LoginView.as_view()),
    url(r'^api/admin/orders/$', views.OrdersView.as_view()),  # 订单列表
    url(r'^api/admin/orders/(?P<order_no>\d+)/$', views.OrderDetailView.as_view()),  # 订单详情,修改订单状态
    url(r'^api/admin/orders/(?P<order_no>\d+)/log/$', views.OrderLogsView.as_view()),  # 订单日志
]
