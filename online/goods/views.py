from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
# Create your views here.
from django.template import Template, Context
from django.template.loader import get_template
from django.urls import reverse
from django.views import View

from online.goods.models import Category,Goods
from online.logger import online_logger
from weigan_shopping import settings
from online.constants import PER_PAGE_GOODS_COUNT


def make(request):
    a = '123456'
    b = make_password(a,hasher='unsalted_md5')
    print(b)
    return HttpResponse("ok")



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
        if len(goods) == 1:
            goods = goods[0]
            goods_list = [{"id": goods.id, "name": goods.name_en, "price": goods.price,
                           "is_hot": goods.is_hot, "image": settings.URL_PREFIX + goods.image.url}]
        else:
            for single_goods in goods:
                goods_list.append({"id":single_goods.id,"name":single_goods.name_en,"price":single_goods.price,"is_hot":single_goods.is_hot,"image":settings.URL_PREFIX + single_goods.image.url})
    context = {"category":category,"goods":goods_list}
    return render(request,"index.html",context=context)


class GoodsListView(View):

    def get(self,request,type):
        current = request.GET.get("current", 0)
        count = PER_PAGE_GOODS_COUNT if current != 0 else 6
        try:
            current = int(current)
            if type == 'hot':
                goods = Goods.objects.order_by('-sale')[current:current+count]
            elif type == 'new':
                goods = Goods.objects.order_by('-added_time')[current:current + count]
            else:
                return JsonResponse({"errcode":"108","errmsg":"illegal request"})
        except TypeError as e:
            online_logger.error(e)
            return JsonResponse({"errcode":"101","errmsg":"params error"})
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode":"102","errmsg":"db error"})
        goods_list = []
        if goods is None:
            goods_list = []
        else:
            if len(goods) == 1:
                goods = goods[0]
                goods_list = [{"id": goods.id, "name": goods.name_en, "price": goods.price,
                              "is_hot": goods.is_hot,"image":settings.URL_PREFIX+goods.image.url}]
            else:
                for single_goods in goods:
                    goods_list.append({"id": single_goods.id, "name": single_goods.name_en, "price": single_goods.price,
                                  "is_hot": single_goods.is_hot,"image":settings.URL_PREFIX+single_goods.image.url})
        result = {"goods": goods_list}
        t = get_template("goods_block.html")
        result = t.render(result)
        return HttpResponse(result)


class GoodsCategoryView(View):

    def get(self,request,category_id):
        current = request.GET.get("current", 0)
        # if current == 0:
        #     return redirect("")
        count = PER_PAGE_GOODS_COUNT
        try:
            current = int(current)
            goods = Goods.objects.filter(category__id=category_id).order_by('-sale')[current:current+count]
        except TypeError as e:
            online_logger.error(e)
            return JsonResponse({"errcode":"101","errmsg":"params error"})
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode":"102","errmsg":"db error"})
        goods_list = []
        if goods is None:
            goods_list = []
        else:
            if len(goods) == 1:
                goods = goods[0]
                goods_list = [{"id": goods.id, "name": goods.name_en, "price": goods.price,
                              "is_hot": goods.is_hot,"image":settings.URL_PREFIX + goods.image.url}]
            else:
                for single_goods in goods:
                    goods.append({"id": single_goods.id, "name": single_goods.name_en, "price": single_goods.price,
                                  "is_hot": single_goods.is_hot,"image":settings.URL_PREFIX + single_goods.image.url})
        result = {"goods": goods_list}
        t = get_template("goods_block.html")
        result = t.render(result)
        return HttpResponse(result)


class GoodsCategoryTemplateView(View):

    def get(self,request,category_id):
        count = PER_PAGE_GOODS_COUNT
        try:
            goods = Goods.objects.filter(category__id=category_id).order_by('-sale')[:count]
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        goods_list = []
        if goods is None:
            goods_list = []
        else:
            if len(goods) == 1:
                goods = goods[0]
                goods_list = [{"id": goods.id, "name": goods.name_en, "price": goods.price,
                               "is_hot": goods.is_hot, "image": settings.URL_PREFIX + goods.image.url}]
            else:
                for single_goods in goods:
                    goods.append({"id": single_goods.id, "name": single_goods.name_en, "price": single_goods.price,
                                  "is_hot": single_goods.is_hot, "image": settings.URL_PREFIX + single_goods.image.url})
        context = {"goods": goods_list}
        return render(request,"goodsList.html",context=context)


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
        # return render(request,"detail.html",context=context)


class GoodsSearchView(View):
    def get(self,request):
        keyword = request.GET.get("keyword",None)
        current = request.GET.get("current", 0)
        count = 9 if current != 0 else 6
        if keyword is None:
            return JsonResponse({"errcode":"101","errmsg":"empty params"})
        try:
            goods = Goods.objects.filter(name_en__contains=keyword)[current:current+count]
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        goods_list = []
        if goods is None:
            goods_list = []
        else:
            if len(goods) == 1:
                goods = goods[0]
                goods_list = [{"id": goods.id, "name": goods.name_en, "price": goods.price,
                               "is_hot": goods.is_hot, "image": settings.URL_PREFIX + goods.image.url}]
            else:
                for single_goods in goods:
                    goods.append({"id": single_goods.id, "name": single_goods.name_en, "price": single_goods.price,
                                  "is_hot": single_goods.is_hot, "image": settings.URL_PREFIX + single_goods.image.url})
        result = {"goods": goods_list}
        t = get_template("goods_block.html")
        result = t.render(result)
        return HttpResponse(result)

