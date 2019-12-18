from django.conf.urls import url

from online.goods import views

urlpatterns = [
    url(r'^index/$', views.index),
    url(r'^goods/category/(?P<category_id>\d+)/$',views.GoodsCategoryTemplateView.as_view(),name='category_template'),
    url(r'^api/goods/category/(?P<category_id>\d+)/$',views.GoodsCategoryView.as_view()),
    url(r'^goods/(?P<goods_id>\d+)/$',views.GoodsView.as_view()),
    url(r'^api/goods/search/$',views.GoodsSearchView.as_view()),
    url(r'^api/goods/(?P<type>(hot)|(new))/$', views.GoodsListView.as_view()),
]