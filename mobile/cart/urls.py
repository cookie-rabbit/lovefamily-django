from django.conf.urls import url

from online.cart import views

urlpatterns = [
    url(r'^carts/',views.CartsView.as_view()),
    url(r'^api/carts/',views.CartsView.as_view()),
    url(r'^api/cart/(?P<cart_id>\d+)/$',views.CartView.as_view()),
]