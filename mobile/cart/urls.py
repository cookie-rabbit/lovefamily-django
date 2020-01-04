from django.conf.urls import url

from mobile.cart import views

urlpatterns = [
    url(r'^api/mobile/carts/', views.CartsView.as_view()),  # 新增，获取购物车列表
    url(r'^api/mobile/cart/(?P<cart_id>\d+)/$', views.CartView.as_view()),  # 修改，删除购物车记录
]
