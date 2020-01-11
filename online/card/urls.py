from django.conf.urls import url, include

from online.card import views

urlpatterns = [
    url(r'^paypal/', include('paypal.standard.ipn.urls')),
    url(r'^paypals/$', views.PaymentView.as_view()),
]
