import json

from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
# Create your views here.
from django.template import Template, Context
from django.template.loader import get_template
from django.urls import reverse
from django.views import View

from management.user.models import User
from online.goods.models import Category, Goods, Image
from online.logger import online_logger
from online.order.models import Order
from weigan_shopping import settings
from online.constants import PER_PAGE_GOODS_COUNT



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

    count = 1
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
            image = Image.objects.filter(goods=single_goods,is_default=True)
            goods_list.append({"id": single_goods.id, "name": single_goods.name_en, "price": single_goods.on_price,
                               "is_hot": single_goods.is_hot, "image": settings.URL_PREFIX + image[0].image.url})
    user_id = request.session.get("user_id",None)
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            orders = Order.objects.filter(user = user)
            order_quantity = len(orders)
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode":"102","errmsg":"db error"})
        cart_quantity = request.session.get("%s_cart" % user_id,0)
        context = {"category":category,"goods":goods_list,"user":user.username,"cart_quantity":cart_quantity,"order_quantity":order_quantity}
    else:
        context = {"category": category, "goods": goods_list,"user":"","cart_quantity":0,"order_quantity":0}
    return render(request,"index.html",context=context)


class GoodsTypeView(View):

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
            for single_goods in goods:
                image = Image.objects.filter(goods=single_goods, is_default=True)
                goods_list.append({"id": single_goods.id, "name": single_goods.name_en, "price": single_goods.on_price,
                                   "is_hot": single_goods.is_hot, "image": settings.URL_PREFIX + image[0].image.url})
        result = {"goods": goods_list}
        t = get_template("goods_block.html")
        result = t.render(result)
        return JsonResponse({"errcode":"0","data":result})


class GoodsCategoryView(View):

    def get(self,request,category_id):
        current = request.GET.get("current", 0)
        if current == 0:
            return redirect(reverse("category_template",args=category_id))
        count = PER_PAGE_GOODS_COUNT
        try:
            category_id = int(category_id)
            current_category = Category.objects.get(id=category_id)
            if current_category.super_category:
                goods = Goods.objects.filter(category__id=category_id).order_by('-sale')[:count]
            else:
                categories = Category.objects.filter(super_category=current_category)
                goods = Goods.objects.filter(category__in=categories).order_by('-sale')[:count]
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
            for single_goods in goods:
                image = Image.objects.filter(goods=single_goods, is_default=True)
                goods_list.append({"id": single_goods.id, "name": single_goods.name_en, "price": single_goods.on_price,
                                   "is_hot": single_goods.is_hot, "image": settings.URL_PREFIX + image[0].image.url})
        result = {"goods": goods_list}
        t = get_template("goods_block.html")
        result = t.render(result)
        return JsonResponse({"errcode":"0","data":result})


class GoodsCategoryTemplateView(View):

    def get(self,request,category_id):
        category = []
        try:
            cates = Category.objects.filter(super_category__isnull=True)
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        for cate in cates:
            try:
                sub_cates = Category.objects.filter(super_category__id=cate.id)
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "db error"})
            category.append({"id": cate.id, "name": cate.name,
                             "sub_cates": [{'id': sub_cate.id, 'name': sub_cate.name} for sub_cate in sub_cates if
                                           sub_cates] if sub_cates else []})

        count = PER_PAGE_GOODS_COUNT
        try:
            category_id = int(category_id)
            current_category = Category.objects.get(id=category_id)
            if current_category.super_category:
                goods = Goods.objects.filter(category__id=category_id).order_by('-sale')[:count]
                super_category = {"id":current_category.super_category.id,"name":current_category.super_category.name}
            else:
                categories = Category.objects.filter(super_category=current_category)
                goods = Goods.objects.filter(category__in=categories).order_by('-sale')[:count]
                super_category = ""
        except TypeError as e:
            online_logger.error(e)
            return JsonResponse({"errcode":"101","errmsg":"params error"})
        except Category.DoesNotExist as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "can not find category in db"})
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})

        goods_list = []
        if goods is None:
            goods_list = []
        else:
            for single_goods in goods:
                image = Image.objects.filter(goods=single_goods, is_default=True)
                goods_list.append({"id": single_goods.id, "name": single_goods.name_en, "price": single_goods.on_price,
                                   "is_hot": single_goods.is_hot, "image": settings.URL_PREFIX + image[0].image.url})
        user_id = request.session.get("user_id", None)
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                orders = Order.objects.filter(user=user)
                order_quantity = len(orders)
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "db error"})
            cart_quantity = request.session.get("%s_cart" % user_id, 0)
            context = {"category": category,"goods": goods_list, "user": user.username, "cart_quantity": cart_quantity,
                       "order_quantity": order_quantity}
        else:
            context = {"category": category, "goods": goods_list, "user": "", "cart_quantity": 0, "order_quantity": 0}

        context.update({"current_category":{"super_category":super_category,"category":{"id": current_category.id, "name": current_category.name}}})
        print(context)
        return render(request,"goodsList.html",context=context)


class GoodsTemplateView(View):

    def get(self,request,goods_id):
        category = []
        try:
            cates = Category.objects.filter(super_category__isnull=True)
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        for cate in cates:
            try:
                sub_cates = Category.objects.filter(super_category__id=cate.id)
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "db error"})
            category.append({"id": cate.id, "name": cate.name,
                             "sub_cates": [{'id': sub_cate.id, 'name': sub_cate.name} for sub_cate in sub_cates if
                                           sub_cates] if sub_cates else []})
        try:
            single_goods = Goods.objects.get(id=goods_id)
            images = Image.objects.filter(goods__id=goods_id)
        except Goods.DoesNotExist as e:
            online_logger.error(e)
            return JsonResponse({"errcode":"102","errmsg":"can not find goods in db"})
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode":"102","errmsg":"db error"})
        goods_detail = {"id":single_goods.id,
                   "name":single_goods.name_en,
                   "images":[settings.URL_PREFIX  + goods_image.image.url for goods_image in images],
                   "origin_price":single_goods.origin_price,
                   "on_price":single_goods.on_price,
                   "sale":single_goods.sale,
                   "detail":single_goods.detail_en,
                   "description":single_goods.description_en}
        user_id = request.session.get("user_id", None)
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                orders = Order.objects.filter(user=user)
                order_quantity = len(orders)
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "db error"})
            cart_quantity = request.session.get("%s_cart" % user_id, 0)
            context = {"category": category, "goods": goods_detail, "user": user.username, "cart_quantity": cart_quantity,
                       "order_quantity": order_quantity}
        else:
            context = {"category": category, "goods": goods_detail, "user": "", "cart_quantity": 0, "order_quantity": 0}
        # return JsonResponse(context)
        return render(request,"detail.html",context=context)


class GoodsSearchView(View):
    def get(self,request):
        keyword = request.GET.get("keyword",None)
        current = request.GET.get("current", 0)
        count = PER_PAGE_GOODS_COUNT
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
            for single_goods in goods:
                image = Image.objects.filter(goods=single_goods, is_default=True)
                goods_list.append({"id": single_goods.id, "name": single_goods.name_en, "price": single_goods.on_price,
                                   "is_hot": single_goods.is_hot, "image": settings.URL_PREFIX + image[0].image.url})
        result = {"goods": goods_list}
        t = get_template("goods_block.html")
        result = t.render(result)
        return JsonResponse({"errcode":"0","data":result})


class GoodsSearchTemplateView(View):

    def get(self,request):
        keyword = request.GET.get("keyword", None)
        count = PER_PAGE_GOODS_COUNT
        if keyword is None:
            return JsonResponse({"errcode": "101", "errmsg": "empty params"})
        try:
            goods = Goods.objects.filter(name_en__contains=keyword)[:count]
        except TypeError as e:
            online_logger.error(e)
            return JsonResponse({"errcode":"101","errmsg":"params error"})
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        goods_list = []
        if goods is None:
            goods_list = []
        else:
            for single_goods in goods:
                image = Image.objects.filter(goods=single_goods, is_default=True)
                goods_list.append({"id": single_goods.id, "name": single_goods.name_en, "price": single_goods.on_price,
                                   "is_hot": single_goods.is_hot, "image": settings.URL_PREFIX + image[0].image.url})
        goods_list = {"goods": goods_list}
        category = []
        try:
            cates = Category.objects.filter(super_category__isnull=True)
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        for cate in cates:
            try:
                sub_cates = Category.objects.filter(super_category__id=cate.id)
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "db error"})
            category.append({"id": cate.id, "name": cate.name,
                             "sub_cates": [{'id': sub_cate.id, 'name': sub_cate.name} for sub_cate in sub_cates if
                                           sub_cates] if sub_cates else []})
        user_id = request.session.get("user_id", None)
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                orders = Order.objects.filter(user=user)
                order_quantity = len(orders)
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "db error"})
            cart_quantity = request.session.get("%s_cart" % user_id, 0)
            context = {"category": category, "goods": goods_list, "user": user.username, "cart_quantity": cart_quantity,
                       "order_quantity": order_quantity}
        else:
            context = {"category": category, "goods": goods_list, "user": "", "cart_quantity": 0, "order_quantity": 0}
        # return JsonResponse({"errcode": "0", "data": result})
        return render(request,"search.html",context=context)