from django.conf.urls import url

from online.goods import views

urlpatterns = [
    url(r'^api/mobile/index/$', views.index,name='index'),
    url(r'^goods/category/(?P<category_id>\d+)/$',views.GoodsCategoryTemplateView.as_view(),name='category_template'),
    url(r'^api/goods/category/(?P<category_id>\d+)/$',views.GoodsCategoryView.as_view()),
    url(r'^goods/(?P<goods_id>\d+)/$',views.GoodsTemplateView.as_view()),
    url(r'^api/goods/search/$',views.GoodsSearchView.as_view()),
    url(r'^goods/search/$',views.GoodsSearchTemplateView.as_view()),
    url(r'^api/goods/(?P<type>(hot)|(new))/$', views.GoodsTypeView.as_view()),
]