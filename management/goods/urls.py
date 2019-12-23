from django.conf.urls import url

from management.goods import views

urlpatterns = [
    url(r'^goods/$',views.GoodsView.as_view()),
    url(r'^goods/(?P<goods_id>\d+)/$',views.GoodsDetailView.as_view()),
    url(r'^goods/(?P<goods_id>\d+)/settings/$',views.GoodsSettingView.as_view()),
    url(r'^category/$',views.CategoriesView.as_view()),
    url(r'category/(?P<category_id>\d+)/$',views.CategoryView.as_view())
]