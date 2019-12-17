from django.conf.urls import url

from online.goods import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^goods/hot/',views.GoodsHotView.as_view()),
    url(r'^goods/new/',views.GoodsNewView.as_view()),
    url(r'^goods/(?P<category_id>\d+)/$',views.GoodsCategoryView.as_view()),
    url(r'^goods/(?P<goods_id>\d+)/detail/$',views.GoodsView.as_view())
]