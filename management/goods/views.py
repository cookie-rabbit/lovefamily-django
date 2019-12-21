from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.utils.decorators import method_decorator
from django.views import View

from management.constants import PER_PAGE_GOODS_COUNT
from management.logger import management_logger
from online.goods.models import Goods
from utils.decorator import admin_auth


class GoodsView(View):
    @method_decorator(admin_auth)
    def get(self,request,user):
        """获取商品列表"""
        page = request.GET.get("page",1)
        try:
            page = int(page)
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({{"errcode": "101", "errmsg": "params errror"}})
        search_dict = {}
        try:
            goods = Goods.objects.filter(**search_dict)
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        paginator = Paginator(goods, PER_PAGE_GOODS_COUNT)
        goods_list = paginator.page(page)
        result = [{"id": goods.id, "name":goods.name_en,"price":goods.on_price} for goods in goods_list]
        return JsonResponse({"errcode": "0", "data": result})


