from django.conf.urls import url

from mobile.goods import views

urlpatterns = [
    url(r'^api/mobile/index/$', views.index, name='index'),  # 获取首页头图
    url(r'^api/mobile/goods/(?P<goods_id>\d+)/$', views.GoodsTemplateView.as_view()),  # 获取商品详情
    url(r'^api/mobile/goods/$', views.GoodsTypeView.as_view()),  # 获取商品列表
    url(r'^api/mobile/categories/$', views.CategoriesView.as_view()),  # 获取分类
    url(r'^api/mobile/search/$', views.GoodsSearchView.as_view()),  # 获取分类


]
