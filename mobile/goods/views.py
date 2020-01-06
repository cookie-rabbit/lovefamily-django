from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View

from management.user.models import User
from online.goods.models import Category, Goods, Image
from online.logger import online_logger
from online.order.models import Order
from utils.decorator import user_auth
from weigan_shopping import settings
from online.constants import PER_PAGE_GOODS_COUNT, INDEX_GOODS_COUNT


def index(request):
    """首页"""
    img = settings.URL_PREFIX + "/media/index.jpg"
    data = {"img": img}
    return JsonResponse({"errcode": "0", "data": data})



class GoodsTypeView(View):
    """获取热销、新品，分类商品"""

    def get(self, request):
        category_id = request.GET.get("category_id", 0)
        type = request.GET.get("type", 0)
        current = request.GET.get("current", 0)
        if type == "hot" or type == "new":
            count = PER_PAGE_GOODS_COUNT if current != 0 else INDEX_GOODS_COUNT
            try:
                current = int(current)
                if type == 'hot':
                    total_goods = Goods.objects.filter(on_sale=True).order_by(
                        F('actual_sale') + F('virtual_sale')).reverse()
                    goods = total_goods[current:current + count]
                elif type == 'new':
                    total_goods = Goods.objects.filter(on_sale=True).order_by('-added_time')
                    goods = total_goods[current:current + count]
                else:
                    return JsonResponse({"errcode": "108", "errmsg": "illegal request"})
                if len(total_goods) > current + count:
                    more = True
                else:
                    more = False
            except TypeError as e:
                online_logger.error(e)
                return JsonResponse({"errcode": "101", "errmsg": "params error"})
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "db error"})
            goods_list = []
            if goods is None:
                goods_list = []
            else:
                for single_goods in goods:
                    image = Image.objects.filter(goods=single_goods)

                    if type == 'hot':
                        if single_goods.is_hot is True:
                            goods_list.append(
                                {"id": single_goods.id, "name": single_goods.name_en,
                                 "description": single_goods.description_en, "price": single_goods.origin_price,
                                 "on_price": single_goods.on_price,
                                 "is_hot": single_goods.is_hot, "image": settings.URL_PREFIX + image[0].image.url})
                        else:
                            goods_list.append(
                                {"id": single_goods.id, "name": single_goods.name_en,
                                 "description": single_goods.description_en, "price": single_goods.origin_price,
                                 "on_price": single_goods.on_price,
                                 "image": settings.URL_PREFIX + image[0].image.url})

                    elif type == 'new':
                        if single_goods.is_new is True:
                            goods_list.append(
                                {"id": single_goods.id, "name": single_goods.name_en,
                                 "description": single_goods.description_en, "price": single_goods.origin_price,
                                 "on_price": single_goods.on_price,
                                 "is_new": single_goods.is_new, "image": settings.URL_PREFIX + image[0].image.url})
                        else:
                            goods_list.append(
                                {"id": single_goods.id, "name": single_goods.name_en,
                                 "description": single_goods.description_en, "price": single_goods.origin_price,
                                 "on_price": single_goods.on_price,
                                 "image": settings.URL_PREFIX + image[0].image.url})

            return JsonResponse({"errcode": "0", "data": {"item": goods_list, "more": more}})
        elif type == "category":
            count = PER_PAGE_GOODS_COUNT
            try:
                current = int(current)
                category_id = int(category_id)

                total_goods = Goods.objects.filter(on_sale=True).filter(category_id=category_id).order_by(
                    F('actual_sale') + F('virtual_sale'))
                goods = total_goods[current:current + count]
                if len(total_goods) > current + count:
                    more = True
                else:
                    more = False
            except TypeError as e:
                online_logger.error(e)
                return JsonResponse({"errcode": "101", "errmsg": "params error"})
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "db error"})
            goods_list = []
            if goods is None:
                goods_list = []
            else:
                for single_goods in goods:
                    image = Image.objects.filter(goods=single_goods)
                    if single_goods.is_hot is True:
                        goods_list.append(
                            {"id": single_goods.id, "name": single_goods.name_en,
                             "description": single_goods.description_en, "price": single_goods.on_price,
                             "is_hot": single_goods.is_hot, "image": settings.URL_PREFIX + image[0].image.url})
                    elif single_goods.is_new is True:
                        goods_list.append(
                            {"id": single_goods.id, "name": single_goods.name_en,
                             "description": single_goods.description_en, "price": single_goods.on_price,
                             "is_new": single_goods.is_new, "image": settings.URL_PREFIX + image[0].image.url})
                    else:
                        goods_list.append(
                            {"id": single_goods.id, "name": single_goods.name_en,
                             "description": single_goods.description_en, "price": single_goods.on_price,
                             "image": settings.URL_PREFIX + image[0].image.url})

            return JsonResponse({"errcode": "0", "data": {"more": more, "item": goods_list}})


class GoodsTemplateView(View):
    """获取商品详情"""

    @method_decorator(user_auth)
    def get(self, request, goods_id, user):
        try:
            single_goods = Goods.objects.get(id=goods_id)
            images = Image.objects.filter(goods__id=goods_id)
        except Goods.DoesNotExist as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "can not find goods in db"})
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        goods_detail = {"id": single_goods.id,
                        "name": single_goods.name_en,
                        "images": [settings.URL_PREFIX + goods_image.image.url for goods_image in images],
                        "origin_price": single_goods.origin_price,
                        "on_price": single_goods.on_price,
                        "sale": single_goods.actual_sale + single_goods.virtual_sale,
                        "detail": single_goods.detail_en,
                        "description": single_goods.description_en}
        user_id = user.id
        if user_id:
            cart_quantity = request.session.get("%s_cart" % user_id, 0)
            context = {"goods": goods_detail, "cart_quantity": cart_quantity}
        else:
            context = {"goods": goods_detail, "cart_quantity": 0}
        return JsonResponse({"errcode": "0", "data": context})


class CategoriesView(View):
    @method_decorator(user_auth)
    def get(self, request, user):
        """获取分类"""
        category = []
        try:
            cates = Category.objects.filter(super_category__isnull=True).filter(disabled=0)
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        for cate in cates:
            quantity = 0
            try:
                sub_cates = Category.objects.filter(super_category__id=cate.id)
                sub_cate_info = []
                if len(sub_cates) > 0:
                    for sub_cate in sub_cates:
                        sub_quantity = len(Goods.objects.filter(category=sub_cate))
                        quantity += sub_quantity
                        sub_cate_info.append({'id': sub_cate.id, 'name': sub_cate.name, "quantity": sub_quantity})
                quantity += len(Goods.objects.filter(category=cate))
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "db error"})
            category.append({"id": cate.id, "name": cate.name, "quantity": quantity,
                             "sub_cates": sub_cate_info})
        return JsonResponse({"errcode": 0, "data": category})


class GoodsSearchTemplateView(View):
    @method_decorator(user_auth)
    def get(self, request, user):
        keyword = request.GET.get("keyword", None)
        count = PER_PAGE_GOODS_COUNT
        if keyword is None:
            return JsonResponse({"errcode": "101", "errmsg": "empty params"})
        try:
            total_goods = Goods.objects.filter(on_sale=True).filter(name_en__contains=keyword)
            goods = total_goods[:count]
            if len(total_goods) > count:
                more = True
            else:
                more = False
        except TypeError as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "101", "errmsg": "params error"})
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        goods_list = []
        if goods is None:
            goods_list = []
        else:
            for single_goods in goods:
                image = Image.objects.filter(goods=single_goods)
                goods_list.append({"id": single_goods.id, "name": single_goods.name_en, "price": single_goods.on_price,
                                   "is_hot": single_goods.is_hot, "is_new": single_goods.is_new,
                                   "image": settings.URL_PREFIX + image[0].image.url})
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
        user_id = user.id
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                orders = Order.objects.filter(user=user)
                order_quantity = len(orders)
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "db error"})
            cart_quantity = request.session.get("%s_cart" % user_id, 0)
            context = {"category": category, "goods": goods_list, "user": user, "cart_quantity": cart_quantity,
                       "order_quantity": order_quantity, "keyword": keyword, "more": more}
        else:
            context = {"category": category, "goods": goods_list, "user": "", "cart_quantity": 0, "order_quantity": 0,
                       "keyword": keyword, "more": more}
        return render(request, "searchResult.html", context=context)