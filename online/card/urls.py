from django.conf.urls import url, include

from online.card import views

urlpatterns = [
    url(r'^paypal/$', views.PaymentView.as_view()),
    url(r'^paypals/$', views.CheckView.as_view()),
]
