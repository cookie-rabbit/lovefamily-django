from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
# Create your views here.
from django.views import View

from online.goods.models import Category,Goods
from online.logger import online_logger
from weigan_shopping import settings


def index(request):
    category = []
    try:
        cates = Category.objects.filter(super_category__isnull = True)
    except Exception as e:
        online_logger.error(e)
        return JsonResponse({"errcode":"102","errmsg":"db error"})
    for cate in cates:
        try:
            sub_cates = Category.objects.filter(super_category__id = cate.id)
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode":"102","errmsg":"db error"})
        category.append({"id":cate.id,"name":cate.name,"sub_cates":[{'id':sub_cate.id,'name':sub_cate.name} for sub_cate in sub_cates if sub_cates ] if sub_cates else []})
    print(category)

    count = 6
    try:
        goods = Goods.objects.order_by('-sale')[:count]
    except Exception as e:
        online_logger.error(e)
        return JsonResponse({"errcode":"102","errmsg":"db error"})
    goods_list = []
    if goods is None:
        goods_list = []
    else:
        for single_goods in goods:
            goods.append({"id":single_goods.id,"name":single_goods.name_en,"price":single_goods.price,"is_hot":single_goods.is_hot,"image":single_goods.image})
    context = {"category":category,"goods":goods_list}
    return render(request,"index.html",context=context)


class GoodsHotView(View):

    def get(self,request):
        current = request.GET.get("current",0)
        count = 9
        try:
            goods = Goods.objects.order_by('-sale')[current:current+count]
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode":"102","errmsg":"db error"})
        goods_list = []
        if goods is None:
            goods_list = []
        else:
            for single_goods in goods:
                goods.append({"id": single_goods.id, "name": single_goods.name_en, "price": single_goods.price,
                              "is_hot": single_goods.is_hot,"image":single_goods.image})
        result = {"goods": goods_list}
        return JsonResponse({"errcode":"0","result":result})


class GoodsNewView(View):

    def get(self,request):
        current = request.GET.get("current", 0)
        count = 9 if current != 0 else 6
        try:
            goods = Goods.objects.order_by('-added_time')[current:current + count]
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        goods_list = []
        if goods is None:
            goods_list = []
        else:
            for single_goods in goods:
                goods.append({"id": single_goods.id, "name": single_goods.name_en, "price": single_goods.price,
                              "is_hot": single_goods.is_hot,"image":single_goods.image})
        result = {"goods": goods_list}
        return JsonResponse({"errcode": "0", "result": result})


class GoodsCategoryView(View):

    def get(self,request,category_id):
        current = request.GET.get("current", 0)
        count = 9 if current != 0 else 6
        try:
            goods = Goods.objects.filter(category__id=category_id).order_by('-sale')[current:current+count]
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode":"102","errmsg":"db error"})
        goods_list = []
        if goods is None:
            goods_list = []
        else:
            for single_goods in goods:
                goods.append({"id": single_goods.id, "name": single_goods.name_en, "price": single_goods.price,
                              "is_hot": single_goods.is_hot,"image":single_goods.image})
        result = {"goods": goods_list}
        return JsonResponse({"errcode": "0", "result": result})


class GoodsView(View):

    def get(self,request,goods_id):
        try:
            single_goods = Goods.objects.get(id=goods_id)
        except Goods.DoesNotExist as e:
            online_logger.error(e)
            return JsonResponse({"errcode":"102","errmsg":"can not find goods in db"})
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode":"102","errmsg":"db error"})
        context = {"id":single_goods.id,
                   "name":single_goods.name_en,
                   "image":settings.URL_PREFIX + single_goods.image.url,
                   "price":single_goods.price,
                   "sale":single_goods.sale,
                   "detail":single_goods.detail_en,
                   "description":single_goods.description_en}
        return JsonResponse(context)
        # return render(request,"goods_detail.html",context=context)

