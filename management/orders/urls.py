from django.conf.urls import url
from management.orders import views

urlpatterns = [
    # url(r'^login/',views.LoginView.as_view()),
    url(r'^admin/orders/{order_id}', views.OderStatusChange.as_view()),
    url(r'^api/admin/orders/', views.OrdersView.as_view()),

]
