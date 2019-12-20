from django.db import transaction
from django.shortcuts import render
from django.template.loader import get_template
from django.utils.decorators import method_decorator
from django.http import JsonResponse, QueryDict, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import django.db as db

from online.constants import PER_PAGE_GOODS_COUNT
from online.order.models import Order, Order_Goods, OrderAddress
from online.goods.models import Goods, Image
from management.user.models import User
from online.logger import online_logger
from utils.decorator import user_auth
from online.cart.models import Cart
from management.user.models import UserAddress

import ast
import random
from datetime import datetime, timedelta
import json


# 【渲染】订单页面（地址）
class OrderAddressView(View):
    @method_decorator(user_auth)
    def get(self, request, user):
        user_id = user.id
        good_dict = []
        total = 0

        try:
            user = UserAddress.objects.get(id=user_id)
            if user != '':
                name = user.name
                province = user.province
                city = user.city
                district = user.district
                road = user.road
                phone_number = user.phone_number
                postcode = user.postcode
                user_info = {"name": name, "province": province, "city": city, "district": district,
                             "road": road, "phone_number": phone_number, "postcode": postcode}

            else:
                return JsonResponse({"errcode": 19, "errmsg": "用户不存在"})

            carts = Cart.objects.filter(user_id=user_id)
            for cart in carts:
                good_id = cart.goods_id
                quantity = cart.quantity
                try:
                    good_detail = Goods.objects.get(id=good_id)
                    good_name_en = good_detail.name_en
                    good_price = good_detail.on_price
                    good_description_en = good_detail.description_en
                    good_image = str(Image.objects.filter(goods_id=good_id)[0].image)
                    good_dict.append({"id": good_id, "quantity": quantity, "name_en": good_name_en, "price": good_price,
                                      "description_en": good_description_en, "image": good_image})
                    total = total + quantity * good_price

                except Exception as e:
                    online_logger.error(e)
                    return JsonResponse({"errcode": 10, "errmsg": "数据库错误"})
            res = {"user_info": user_info, "good_dict": good_dict, "total": total}

            tpl = get_template("myOrder.html")
            res = tpl.render(res)
            return HttpResponse(res)

        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": 13, "errmsg": "数据库错误"})


# 订单详情
class OrdersDetailView(View):
    @method_decorator(user_auth)
    def get(self, request, user):
        user_id = user.id
        order_no = request.GET.get('order_no')
        orders = Order.objects.filter(user_id=user_id)
        order = orders.get(order_no=order_no)
        if order != '':
            try:
                goods = Order_Goods.objects.filter(order_id=order.id)
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({"errcode": 13, "errmsg": "数据库错误"})
            if goods != '':
                good_dic = []
                for good in goods:
                    good_id = good.goods_id
                    quantity = good.quantity
                    good_detail = Goods.objects.get(id=good_id)
                    good_name_en = good_detail.name_en
                    good_price = good_detail.on_price
                    good_description_en = good_detail.description_en
                    good_image = str(Image.objects.filter(goods_id=good_id)[0].image)
                    good_dic.append({"id": good_id, "quantity": quantity, "name_en": good_name_en, "price": good_price,
                                     "description_en": good_description_en, "image": good_image})
                res = {"good_dic": good_dic}
                tpl = get_template("orderDetail.html")
                data = tpl.render(res)
                return JsonResponse({'errcode': 0, 'data': data})
            else:
                return JsonResponse({"errcode": 13, "errmsg": "商品不存在"})
        else:
            return JsonResponse({'errcode': 4, 'errmsg': "订单不存在"})


# 【渲染】订单列表
class OrdersListView(View):
    @method_decorator(user_auth)
    def get(self, request, user):
        user_id = user.id
        status_query = request.GET.get('status', 0)

        orders = Order.objects.filter(user_id=user_id).order_by('-order_date')
        try:
            status_query = int(status_query)
        except ValueError as e:
            online_logger.error(e)
            return JsonResponse({'errcode': 1, 'errmsg': "状态码错误"})
        try:
            if status_query == 0:
                orders_total = orders.order_by('-order_date')
            else:
                orders_total = orders.filter(status=status_query).order_by('-order_date')
            orders = orders_total[: PER_PAGE_GOODS_COUNT]

        except Exception as e:
            online_logger.error(e)
            return JsonResponse({'errcode': 4, 'errmsg': "数据格式错误"})
        order_count = orders_total.count()

        if order_count > PER_PAGE_GOODS_COUNT:
            more = 'true'
        else:
            more = 'false'
        if orders.count() > 0:
            order_dic = []
            good_dic = []

            for order in orders:
                order_no = order.order_no
                order_date = order.order_date
                total = order.total
                status = order.get_status_display()
                order_dic.append({"order_no": order_no, "order_date": order_date, "total": total, "status": status})

            try:
                order = orders.first()
                goods = Order_Goods.objects.filter(order_id=order.id)
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({"errcode": 111, "errmsg": "数据库错误"})
            if goods != '':
                for good in goods:
                    good_id = good.goods_id
                    quantity = good.quantity

                    good_detail = Goods.objects.get(id=good_id)
                    good_name_en = good_detail.name_en
                    good_price = good_detail.on_price
                    good_description_en = good_detail.description_en
                    good_image = str(Image.objects.filter(goods_id=good_id)[0].image)
                    good_dic.append({"id": good_id, "quantity": quantity, "name_en": good_name_en, "price": good_price,
                                     "description_en": good_description_en, "image": good_image})
            else:
                return JsonResponse({'errcode': 112, 'errmsg': "商品不存在"})
        else:
            order_dic = []
            good_dic = []
        res = {"order_dic": order_dic, "good_dic": good_dic, "status": status_query, "more": more}
        return render(request, "myOrders.html", context=res)


# 创建订单
class OrderCreateView(View):
    @method_decorator(transaction.atomic)
    @method_decorator(csrf_exempt)
    @method_decorator(user_auth)
    def post(self, request, user):
        try:
            name = request.POST.get('name')
            province = request.POST.get('province')
            city = request.POST.get('city')
            district = request.POST.get('district')
            road = request.POST.get('road')
            postcode = request.POST.get('postcode')
            phone_number = request.POST.get('phone_number')
            goods = ast.literal_eval(request.POST.get('goods'))
            total = request.POST.get('total')
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": 10, "errmsg": "订单信息不完整"})

        user_id = user.id
        if total.isdigit():
            time = timezone.localtime(timezone.now()).strftime("%Y-%m-%d")
            order_no = random.randint(0, 9999999999)
            status = 0

            save_id = transaction.savepoint()
            try:
                order_address = OrderAddress.objects.create(name=name, province=province, road=road,
                                                            city=city, district=district, postcode=postcode,
                                                            phone_number=phone_number)

                order = Order.objects.create(order_no=order_no, total=total, order_date=time, status=status,
                                             address=order_address, user=User.objects.get(id=user_id))
            except db.DataError as e:
                online_logger.error(e)
                return JsonResponse({"errcode": 3, "errmsg": "数据格式错误"})

            for good in goods:
                goods_id = good['good_id']
                good_count = good['good_count']
                try:
                    Goodgoods = Goods.objects.select_for_update().get(id=goods_id)
                except Goods.DoesNotExist as e:
                    transaction.savepoint_rollback(save_id)
                    online_logger.error(e)
                    return JsonResponse({'errcode': 2, 'errmsg': "商品信息错误"})
                except Exception as e:
                    online_logger.error(e)
                    return JsonResponse({'errcode': 2, 'errmsg': '数据库错误'})
                count = int(good_count)

                if Goodgoods.stock < count:
                    transaction.savepoint_rollback(save_id)
                    return JsonResponse({'errcode': 4, 'errmsg': "库存不足"})

                Goodgoods.sale += count
                Goodgoods.stock -= count
                Goodgoods.save()

                goods = Goods.objects.select_for_update().get(id=goods_id)
                Order_Goods.objects.create(order=order, goods=goods, quantity=count)

            return JsonResponse({"errcode": 0, "data": {"result": "订单创建成功", "href": "https://www.baidu.com"}})
        else:
            return JsonResponse({"errcode": 9, "errmsg": "订单信息格式不正确"})


# 翻页
class OrdersOffsetView(View):
    @method_decorator(user_auth)
    def get(self, request, user):
        user_id = user.id
        offset = request.GET.get('offset', 0)
        status_query = request.GET.get('status', 0)

        try:
            offset = int(offset)
            status_query = int(status_query)
        except ValueError as e:
            online_logger.error(e)
            return JsonResponse({'errcode': 1, 'errmsg': "跳过条数格式错误"})
        try:
            if status_query == 0:
                orders_total = Order.objects.filter(user_id=user_id).order_by('-order_date')
            else:
                orders_total = Order.objects.filter(user_id=user_id, status=status_query).order_by('-order_date')
            orders = orders_total[offset:offset + PER_PAGE_GOODS_COUNT]
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({'errcode': 4, 'errmsg': "数据格式错误"})

        if orders.count() > offset + PER_PAGE_GOODS_COUNT:
            more = 'true'
        else:
            more = 'false'
        if orders.count() > 0:
            order_dic = []

            for order in orders:
                order_no = order.order_no
                order_date = order.order_date
                total = order.total
                status = order.get_status_display()
                order_dic.append({"order_no": order_no, "order_date": order_date, "total": total, "status": status})
        else:
            order_dic = []
        res_order = {"order_dic": order_dic}
        tpl = get_template("orderBlock.html")
        res = tpl.render(res_order)
        return JsonResponse({"errcode": 0, "data": {"result": res, "more": more}})


# 下单页面用户地址修改
class UserAddressView(View):
    @method_decorator(transaction.atomic)
    @method_decorator(csrf_exempt)
    @method_decorator(user_auth)
    def post(self, request, user):
        user_id = user.id
        try:
            name = request.POST.get('name')
            province = request.POST.get('province')
            city = request.POST.get('city')
            district = request.POST.get('district')
            road = request.POST.get('road')
            postcode = request.POST.get('postcode')
            phone_number = request.POST.get('phone_number')
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": 10, "errmsg": "订单信息不完整"})
        try:
            UserAddress.objects.filter(user_id=user_id).update(name=name, province=province, road=road,
                                                               city=city, district=district,
                                                               postcode=postcode,
                                                               phone_number=phone_number)
            return JsonResponse({"errcode": 0, "data": {"result": "地址修改成功"}})
        except db.DataError as e:
            online_logger.error(e)
            return JsonResponse({"errcode": 3, "errmsg": "数据格式错误"})


# 【渲染】订单页面（地址）
class OrderPayView(View):
    @method_decorator(user_auth)
    def get(self, request, user):
        pass


# 修改订单状态
class OderStatusChange(View):

    @method_decorator(transaction.atomic)
    @method_decorator(csrf_exempt)
    def put(self, request):
        if request.method == 'PUT':
            if request.body:
                try:
                    put = QueryDict(request.body)
                    order_no = put.get('order_no')
                    status = put.get('status')
                except Exception as e:
                    online_logger.error(e)
                    return JsonResponse({"errcode": 111, "errmsg": "请求数据不全或格式错误"})
                if status.isdigit() and order_no.isdigit():

                    try:
                        order = Order.objects.get(order_no=order_no)
                    except Order.DoesNotExist as e:
                        online_logger.error(e)
                        return JsonResponse({"errcode": 111, "errmsg": "订单不存在"})
                    except Exception as e:
                        online_logger.error(e)
                        return JsonResponse({"errcode": 111, "errmsg": "数据库错误"})

                    else:
                        if order.status == 2:
                            return JsonResponse({"errcode": 222, "errmsg": "订单已完成，不能修改状态"})
                        order = Order.objects.get(order_no=order_no)
                        order.status = status
                        order.save()
                        return JsonResponse({"errcode": 5, "errmsg": "订单状态修改成功"})
                else:
                    return JsonResponse({"errcode": 8, "errmsg": "订单状态或订单号不正确"})
            else:
                return JsonResponse({"errcode": 7, "errmsg": "未收到请求内容或请求方式错误"})
        else:
            return JsonResponse({"errcode": 6, "errmsg": "请求方式错误"})
