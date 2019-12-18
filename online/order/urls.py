from django.conf.urls import include, url
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from online.order import views


urlpatterns = [
    path('api/orders/', views.order_generate, name='make_order'),
    path('orders/', views.orders_list, name='orders'),
    path('change_status/', views.oder_status_change, name='change_oder_status'),
]