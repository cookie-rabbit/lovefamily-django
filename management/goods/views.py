import json

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from PIL import Image

from management.constants import PER_PAGE_GOODS_COUNT
from management.logger import management_logger
from online.goods.models import Goods, Category, Image
from utils.decorator import admin_auth
from weigan_shopping import settings


class GoodsView(View):
    @method_decorator(admin_auth)
    def get(self, request, user):
        """获取商品列表"""
        category = []
        try:
            cates = Category.objects.filter(super_category__isnull=True)
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        for cate in cates:
            try:
                sub_cates = Category.objects.filter(super_category__id=cate.id)
            except Exception as e:
                management_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "db error"})
            category.append({"id": cate.id, "name": cate.name,
                             "sub_cates": [{'id': sub_cate.id, 'name': sub_cate.name} for sub_cate in sub_cates if
                                           sub_cates] if sub_cates else []})
        print(category)
        page = request.GET.get("page", 1)
        name = request.GET.get("name", None)
        category1 = request.GET.get("category1", None)
        category2 = request.GET.get("category2", None)
        on_sale = request.GET.get("on_sale", None)
        try:
            page = int(page)
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({{"errcode": "101", "errmsg": "params errror"}})
        search_dict = {}
        if on_sale is not None:
            search_dict['status'] = on_sale
        if category1 and category2:
            search_dict["category__id"] = category2
        elif category1:
            search_dict["category__super_category__id"] = category1
            search_dict["category__id"] = category1
        else:
            pass
        print(search_dict)
        try:
            if search_dict and name:
                goods = Goods.objects.filter(**search_dict).filter(name_en__contains=name)
                print(goods)
            elif search_dict:
                goods = Goods.objects.filter(**search_dict)
                print(goods)
            elif name:
                goods = Goods.objects.filter(name_en__contains=name)
            else:
                goods = Goods.objects.all()
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        paginator = Paginator(goods, PER_PAGE_GOODS_COUNT)
        goods_list = paginator.page(page)
        result = [{"id": goods.id, "name": goods.name_en, "description": goods.description_en, "price": goods.on_price,
                   "category": goods.category.name, "super_category": goods.category.super_category.name,
                   "sale": goods.actual_sale + goods.virtual_sale, "stock": goods.stock, "on_sale": goods.on_sale} for
                  goods in goods_list]
        return JsonResponse({"errcode": "0", "data": result})

    @method_decorator(admin_auth)
    @method_decorator(csrf_exempt)
    def post(self, request, user):
        """新增商品"""
        data = json.loads(request.body.decode())
        name = data.get("name", None)
        description = data.get("description", None)
        detail = data.get("detail", None)
        image = data.get("images", None)
        on_sale = data.get("on_sale", None)
        added_time = data.get("added_time", None)
        origin_price = data.get("price", None)
        on_price = data.get("on_price", None)
        stock = data.get("stock", None)
        virtual_sale = data.get("virtual_sale", None)
        is_hot = data.get("is_hot", None)
        is_new = data.get("is_new", None)
        if name is None or on_sale is None or added_time is None or origin_price is None or on_price is None or stock is None \
                or virtual_sale is None or is_hot is None or is_new is None:
            return JsonResponse({"errcode": "101", "errmsg": "params error"})
        try:
            goods = Goods.objects.create(name_en=name, detail_en=detail, description_en=description, on_sale=on_sale,
                                         origin_price=origin_price, on_price=on_price,
                                         added_time=added_time, stock=stock, virtual_sale=virtual_sale, is_hot=is_hot,
                                         is_new=is_new)
            image = Image.objects.create(image='', goods=goods)
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        return JsonResponse({"errcode": "0", "errmsg": "create success"})


class GoodsDetailView(View):
    @method_decorator(admin_auth)
    def get(self, request, user, goods_id):
        """获取商品详情"""
        try:
            goods = Goods.objects.get(id=goods_id)
            images = Image.objects.filter(goods=goods)
        except Goods.DoesNotExist as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "can not find goods in db"})
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        result = {"id": goods.id, "name": goods.name_en,
                  "images": [settings.URL_PREFIX + image.image.url for image in images],
                  "description": goods.description_en, "detail": goods.detail_en, "on_sale": goods.on_sale,
                  "added_time": goods.added_time, "price": goods.origin_price, "on_price": goods.on_price,
                  "stock": goods.stock, "virtual_sale": goods.virtual_sale, "is_hot": goods.is_hot,
                  "is_new": goods.is_new}
        return JsonResponse({"errcode": "0", "data": result})

    @method_decorator(admin_auth)
    def put(self, request, user, goods_id):
        """修改商品信息"""
        data = json.loads(request.body.decode())
        name = data.get("name", None)
        description = data.get("description", None)
        detail = data.get("detail", None)
        image = data.get("images", None)
        if not all([name, image]):
            return JsonResponse({"errcode": "101", "errmsg": "params error"})
        try:
            goods = Goods.objects.get(id=goods_id)
            goods.name_en = name
            goods.description_en = description
            goods.detail_en = detail
            goods.save()
        except Goods.DoesNotExist as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        return JsonResponse({"errcode": "0", "errmsg": "update success"})


class GoodsSettingView(View):
    @method_decorator(admin_auth)
    def put(self, request, user, goods_id):
        """修改商品设置"""
        data = json.loads(request.body.decode())
        on_sale = data.get("on_sale", None)
        added_time = data.get("added_time", None)
        origin_price = data.get("price", None)
        stock = data.get("stock", None)
        virtual_sale = data.get("virtual_sale", None)
        is_hot = data.get("is_hot", None)
        is_new = data.get("is_new", None)
        print(on_sale, added_time, origin_price, stock, virtual_sale)
        if on_sale is None or added_time is None or origin_price is None or stock is None \
                or virtual_sale is None or is_hot is None or is_new is None:
            return JsonResponse({"errcode": "101", "errmsg": "params error"})
        try:
            Goods.objects.filter(id=goods_id).update(on_sale=on_sale, added_time=added_time, origin_price=origin_price,
                                                     stock=stock, virtual_sale=virtual_sale, is_hot=is_hot,
                                                     is_new=is_new)
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        return JsonResponse({"errcode": "0", "errmsg": "update success"})


class CategoriesView(View):
    @method_decorator(admin_auth)
    def get(self, request, user):
        """获取分类列表"""
        category = []
        try:
            cates = Category.objects.filter(super_category__isnull=True)
        except Exception as e:
            management_logger.error(e)
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
                management_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "db error"})
            category.append({"id": cate.id, "name": cate.name, "quantity": quantity,
                             "sub_cates": sub_cate_info})
        return JsonResponse({"errcode": 0, "data": category})

    @method_decorator(admin_auth)
    def post(self, request, user):
        """创建分类"""
        data = json.loads(request.body.decode())
        category_name = data.get("category_name", None)
        parent_category_id = data.get("parent_category", None)
        print(parent_category_id)
        if category_name is None:
            return JsonResponse({"errcode": "101", "errmsg": "params error"})
        try:
            if parent_category_id:
                parent_category = Category.objects.get(id=parent_category_id)
                category = Category.objects.create(name=category_name, super_category=parent_category)
            else:
                category = Category.objects.create(name=category_name)
        except Category.DoesNotExist as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "can not find category in db"})
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        return JsonResponse({"errcode": "0", "errmsg": "create success"})


class CategoryView(View):
    @method_decorator(admin_auth)
    def put(self, request, user, category_id):
        """修改分类"""
        data = json.loads(request.body.decode())
        category_name = data.get("category_name", None)
        parent_category_id = data.get("parent_category", None)
        if category_name is None:
            return JsonResponse({"errcode": "101", "errmsg": "params error"})
        try:
            category = Category.objects.get(id=category_id)
            category.name = category_name
            if parent_category_id:
                parent_category = Category.objects.get(id=parent_category_id)
                category.super_category = parent_category
            else:
                category.super_category_id = None
            category.save()
        except Category.DoesNotExist as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "can not find category in db"})
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        return JsonResponse({"errcode": "0", "errmsg": "update success"})


class StatusView(View):
    @method_decorator(admin_auth)
    def put(self, request, user, good_id):
        """修改分类"""
        data = json.loads(request.body.decode())
        status = data.get("status", None)
        if status is None:
            return JsonResponse({"errcode": "101", "errmsg": "params error"})
        try:
            good = Goods.objects.get(id=good_id)
            if status == 1:
                good.on_sale = 1
            else:
                good.on_sale = 0
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "can not find good in db"})
        return JsonResponse({"errcode": "0", "errmsg": "update success"})
