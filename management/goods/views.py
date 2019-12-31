import base64
import json
import time

from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from management.constants import PER_PAGE_GOODS_COUNT
from management.logger import management_logger
from online.goods.models import Goods, Category
from online.goods.models import Image as Images
from utils.decorator import admin_auth
from weigan_shopping import settings


class GoodsView(View):
    @method_decorator(admin_auth)
    def get(self, request, user):
        """获取商品列表"""
        page = request.GET.get("page", 1)
        name = request.GET.get("name", None)
        category1 = request.GET.get("category1", None)
        category2 = request.GET.get("category2", None)
        on_sale = request.GET.get("on_sale", None)
        if on_sale == 'true':
            on_sale = True
        elif on_sale == 'false':
            on_sale = False
        try:
            page = int(page)
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({{"errcode": "101", "errmsg": "params errror"}})
        search_dict = {}
        if on_sale is not None:
            search_dict['on_sale'] = on_sale
        if category1 and category2:
            search_dict["category__id"] = category2
        if category1:
            search_dict["super_category_id"] = category1
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
                goods = Goods.objects.all().order_by('added_time')
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        paginator = Paginator(goods, PER_PAGE_GOODS_COUNT)
        goods_list = paginator.page(page)
        names = []
        for goods in goods_list:
            bbb = goods.category.super_category
            aaa = goods.category.super_category.name
        for goods in goods_list:
            name = goods.name_en
            names.append(name)
        result = [{"id": goods.id, "name": goods.name_en, "description": goods.description_en, "price": goods.on_price,
                   "category": goods.category.name, "super_category": goods.category.super_category.name,
                   "sale": goods.actual_sale + goods.virtual_sale, "stock": goods.stock, "on_sale": goods.on_sale} for
                  goods in goods_list]
        return JsonResponse({"errcode": "0", "data": result})

    @method_decorator(admin_auth)
    @method_decorator(transaction.atomic)
    def post(self, request, user):
        """新增商品"""
        data = json.loads(request.body.decode())
        name = data.get("name", None)
        description = data.get("description", None)
        detail = data.get("detail", None)
        images = data.get("image", None)
        on_sale = data.get("on_sale", None)
        added_time = data.get("added_time", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        category_id = data.get("category_id", None)
        super_category_id = data.get("super_category_id", None)
        origin_price = data.get("price", 0)
        on_price = data.get("on_price", None)
        stock = data.get("stock", None)
        virtual_sale = data.get("virtual_sale", 0)
        is_hot = data.get("is_hot", None)
        is_new = data.get("is_new", None)

        if name is None or on_sale is None or on_price is None or stock is None \
                or is_hot is None or is_new is None or category_id is None or super_category_id is None:
            return JsonResponse({"errcode": "101", "errmsg": "params error"})
        try:
            goods = Goods.objects.create(name_en=name, detail_en=detail, description_en=description, on_sale=on_sale,
                                         origin_price=origin_price, on_price=on_price, category_id=category_id,
                                         added_time=added_time, stock=stock, virtual_sale=virtual_sale, is_hot=is_hot,
                                         is_new=is_new, super_category_id=super_category_id)
            for image in images:
                uid = image['uid']
                url = image['url'].split("base64,")[1]
                type = image['url'].split("image/")[1].split(";base64,")[0]
                timestamp = str(int(time.time()))
                imgdata = base64.b64decode(url)
                file_name = str(uid) + '%s.%s' % (timestamp, type)
                file_url = 'media/%s' % file_name
                file = open(file_url, 'wb')
                file.write(imgdata)
                file.close()
                Images.objects.create(image=file_name, goods=goods)

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
            images = Images.objects.filter(goods=goods)
            super_category_id = Category.objects.filter(id=goods.category_id)[0].super_category_id
        except Goods.DoesNotExist as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "can not find goods in db"})
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        result = {"id": goods.id, "name": goods.name_en, "super_category_id": super_category_id,
                  "category_id": goods.category_id,
                  "images": [{"url": settings.URL_PREFIX + image.image.url, "name": image.image.url.split("/media/")[1]}
                             for image in images],
                  "description": goods.description_en, "detail": goods.detail_en, "on_sale": goods.on_sale,
                  "added_time": goods.added_time, "price": goods.origin_price, "on_price": goods.on_price,
                  "stock": goods.stock, "virtual_sale": goods.virtual_sale, "is_hot": goods.is_hot,
                  "is_new": goods.is_new}
        return JsonResponse({"errcode": "0", "data": result})

    @method_decorator(admin_auth)
    @method_decorator(transaction.atomic)
    def put(self, request, user, goods_id):
        type = request.GET.get("type", None)
        """修改商品信息"""
        if request.body:
            if type == "info":
                data = json.loads(request.body.decode())
                name = data.get("name", None)
                description = data.get("description", None)
                detail = data.get("detail", None)
                images = data.get("image", None)
                if not all([name]):
                    return JsonResponse({"errcode": "101", "errmsg": "params error"})
                try:
                    goods = Goods.objects.get(id=goods_id)
                    goods.name_en = name
                    goods.description_en = description
                    goods.detail_en = detail
                    goods.save()
                    image_ids = []
                    if images is not None:
                        for image in images:
                            status = image['status']
                            uid = image['uid']
                            if status == "ready":
                                url = image['url'].split("base64,")[1]
                                type = image['url'].split("image/")[1].split(";base64,")[0]
                                timestamp = str(int(time.time()))
                                imgdata = base64.b64decode(url)
                                file_name = str(uid) + '%s.%s' % (timestamp, type)
                                file_url = 'media/%s' % file_name

                                file = open(file_url, 'wb')
                                file.write(imgdata)
                                file.close()
                                image_res = Images.objects.create(image=file_name, goods=goods)
                                image_ids.append(image_res.id)
                            elif status == "success":
                                image_res = Images.objects.get(image=image['name'])
                                image_ids.append(image_res.id)
                        image_list = Images.objects.filter(goods=goods)
                        image_origin_ids = []
                        for image_origin in image_list:
                            id = image_origin.id
                            image_origin_ids.append(id)
                        retd = list(set(image_origin_ids).difference(set(image_ids)))
                        images_del = Images.objects.filter(id__in=retd)
                        for image_del in images_del:
                            Images.objects.get(id=image_del.id).delete()

                except Goods.DoesNotExist as e:
                    management_logger.error(e)
                    return JsonResponse({"errcode": "102", "errmsg": "db error"})
                except Exception as e:
                    management_logger.error(e)
                    return JsonResponse({"errcode": "102", "errmsg": "db error"})
                return JsonResponse({"errcode": "0", "errmsg": "update success"})

            elif type == "setting":
                """修改商品设置"""
                data = json.loads(request.body.decode())
                on_sale = data.get("on_sale", None)
                added_time = data.get("added_time", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                on_price = data.get("on_price", None)
                origin_price = data.get("price", None)
                category_id = data.get("category_id", None)
                stock = data.get("stock", None)
                virtual_sale = data.get("virtual_sale", 0)
                is_hot = data.get("is_hot", None)
                is_new = data.get("is_new", None)
                print(on_sale, added_time, origin_price, stock, virtual_sale)
                if on_sale is None or stock is None or is_hot is None or is_new is None or on_price is None or \
                        category_id is None:
                    return JsonResponse({"errcode": "101", "errmsg": "params error"})
                try:
                    Goods.objects.filter(id=goods_id).update(on_sale=on_sale, added_time=added_time,
                                                             origin_price=origin_price,
                                                             stock=stock, virtual_sale=virtual_sale, is_hot=is_hot,
                                                             is_new=is_new, on_price=on_price, category_id=category_id)
                except Exception as e:
                    management_logger.error(e)
                    return JsonResponse({"errcode": "102", "errmsg": "db error"})
                return JsonResponse({"errcode": "0", "errmsg": "update success"})

            elif type == "status":
                """修改商品上下架"""
                data = json.loads(request.body.decode())
                status = data.get("status", None)
                if status is None:
                    return JsonResponse({"errcode": "101", "errmsg": "params error"})
                try:
                    good = Goods.objects.get(id=goods_id)
                    if status == 1:
                        good.on_sale = 1
                    else:
                        good.on_sale = 0
                    good.save()
                except Exception as e:
                    management_logger.error(e)
                    return JsonResponse({"errcode": "102", "errmsg": "can not find good in db"})
                return JsonResponse({"errcode": "0", "errmsg": "update success"})
        else:
            return JsonResponse({"errcode": "101", "errmsg": "params error"})


class CategoriesView(View):
    @method_decorator(admin_auth)
    def get(self, request, user):
        """获取分类"""
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
        parent_category_id = data.get("parent_category_id", None)
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
    def put(self, request, category_id):
        type = request.GET.get("type", None)
        if type == "setting":
            """修改分类"""
            data = json.loads(request.body.decode())
            category_id = int(category_id)
            category_name = data.get("category_name", None)
            parent_category_id = data.get("parent_category_id", None)
            if category_name is None:
                return JsonResponse({"errcode": "101", "errmsg": "params error"})
            try:
                category = Category.objects.get(id=category_id)
                category.name = category_name
                length = len(Category.objects.filter(super_category_id=category_id))
                if length == 0:
                    parent_category = Category.objects.get(id=parent_category_id)
                    if parent_category_id is None:
                        category.super_category_id = None
                    elif parent_category_id and parent_category_id and parent_category_id != category_id:
                        category.super_category = parent_category
                    else:
                        return JsonResponse({"errcode": "113", "errmsg": "can't set it self as a partner category"})
                    category.save()
                else:
                    return JsonResponse(
                        {"errcode": "114",
                         "errmsg": "can't set a partner category as child category which is not null"})

            except Category.DoesNotExist as e:
                management_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "can not find category in db"})
            except Exception as e:
                management_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "db error"})
            return JsonResponse({"errcode": "0", "errmsg": "update success"})
        elif type == "show":
            """设置分类是否不显示,1为不显示，0显示"""
            data = json.loads(request.body.decode())
            category_id = int(category_id)
            category_status = data.get("category_status", 0)
            try:
                category_status = int(category_status)
            except Exception as e:
                management_logger.error(e)
                return JsonResponse({"errcode": "101", "errmsg": "params error"})
            try:
                Category.objects.filter(id=category_id).update(disabled=category_status)

            except Category.DoesNotExist as e:
                management_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "can not find category in db"})
            except Exception as e:
                management_logger.error(e)
                return JsonResponse({"errcode": "102", "errmsg": "db error"})
            return JsonResponse({"errcode": "0", "errmsg": "update success"})

    def delete(self, request, category_id):
        """删除分类"""
        try:
            category_id = int(category_id)
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "101", "errmsg": "params error"})

        try:
            category = Category.objects.get(id=category_id)
            length = len(Category.objects.filter(super_category_id=category_id))
            if length == 0:
                leng = len(Goods.objects.filter(category_id=category_id))
                if leng == 0:
                    category.delete()
                    return JsonResponse({"errcode": "0", "errmsg": "deleted success"})
                else:
                    return JsonResponse({"errcode": "102", "errmsg": "can not delete a category which has goods"})
            else:
                return JsonResponse({"errcode": "102", "errmsg": "can not delete a category which has child categoris"})

        except Category.DoesNotExist as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "can not find category in db"})
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})


class CategoriesListView(View):
    @method_decorator(admin_auth)
    def get(self, request, user):
        """获取所有分类列表"""
        category = []
        try:
            cates = Category.objects.all()
        except Exception as e:
            management_logger.error(e)
            return JsonResponse({"errcode": "102", "errmsg": "db error"})
        for cate in cates:
            quantity = 0
            parent_name = ''
            disabled = cate.disabled
            if disabled == 0:
                disabled = False
            elif disabled == 1:
                disabled = True
            if cate.super_category_id is None:
                try:
                    level = 1
                    sub_cates = Category.objects.filter(super_category__id=cate.id)
                    if len(sub_cates) > 0:
                        for sub_cate in sub_cates:
                            sub_quantity = len(Goods.objects.filter(category=sub_cate))
                            quantity += sub_quantity
                            # sub_cate_info.append({'id': sub_cate.id, 'name': sub_cate.name, "quantity": sub_quantity})
                    quantity += len(Goods.objects.filter(category=cate))
                except Exception as e:
                    management_logger.error(e)
                    return JsonResponse({"errcode": "102", "errmsg": "db error"})
            else:
                try:
                    level = 2
                    parent_name = ''
                    super_cates = Category.objects.filter(id=cate.super_category_id)
                    quantity = len(Goods.objects.filter(category=cate.id))
                    if len(super_cates) > 0:
                        parent_name = super_cates[0].name
                        # sub_cate_info.append({'id': sub_cate.id, 'name': sub_cate.name, "quantity": sub_quantity})
                    else:
                        return JsonResponse({"errcode": "102", "errmsg": "the sub_category has no super_category"})
                except Exception as e:
                    management_logger.error(e)
                    return JsonResponse({"errcode": "102", "errmsg": "db error"})
            category.append(
                {"category_id": cate.id, "category_name": cate.name, "goods_total": quantity, "category_level": level,
                 "parent_name": parent_name, "disabled": disabled})
        return JsonResponse({"errcode": 0, "data": category})
