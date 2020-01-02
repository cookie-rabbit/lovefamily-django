from django.conf.urls import url

from online.goods import views

urlpatterns = [
    url(r'^index/$', views.index, name='index'),
    url(r'^api/mobile/goods/(?P<goods_id>\d+)/$', views.GoodsTemplateView.as_view()),  # 商品详情
    url(r'^api/mobile/goods/$', views.GoodsTypeView.as_view()),  # 商品列表
]
