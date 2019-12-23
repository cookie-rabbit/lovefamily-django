from django.conf.urls import url

from management.goods import views

urlpatterns = [
    url(r'^api/admin/goods/$', views.GoodsView.as_view()),
    url(r'^api/admin/goods/(?P<goods_id>\d+)/$', views.GoodsDetailView.as_view()),
    url(r'^api/admin/goods/(?P<goods_id>\d+)/settings/$', views.GoodsSettingView.as_view()),
    url(r'^api/admin/category/$', views.CategoriesView.as_view()),
    url(r'^api/admin/category/(?P<category_id>\d+)/$', views.CategoryView.as_view()),
    url(r'^/api/admin/goods/(?P<good_id>\d+)/status/$', views.StatusView.as_view())

]
