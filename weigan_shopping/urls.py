"""weigan_shopping URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.static import serve
from django.conf.urls.i18n import i18n_patterns

from weigan_shopping.settings import MEDIA_ROOT

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),
    url(r'^', include("online.account.urls")),
    url(r'^', include("online.cart.urls")),
    url(r'^', include("online.goods.urls")),
    url(r'^', include("online.order.urls")),
    url(r'^', include("management.goods.urls")),
    url(r'^', include("management.orders.urls")),
    url(r'^', include("management.user.urls")),
    url(r'^admin/', include("management.user.urls")),
]
