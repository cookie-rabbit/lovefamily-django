from django.conf.urls import url

from online.cart import views

urlpatterns = [
    url(r'^carts/$', views.CartsView.as_view()),  # 【渲染]获取购物车列表
    url(r'^api/carts/$', views.CartsView.as_view()),  # 新增到购物车
    url(r'^api/cart/(?P<cart_id>\d+)/$', views.CartView.as_view()),  # 修改购物车数量
    url(r'^api/carts/confirm/$', views.CartsConfirm.as_view()),  # 提交购物车信息
]
