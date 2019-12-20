from django.db import transaction
from django.shortcuts import render
from django.template.loader import get_template
from django.utils.decorators import method_decorator
from django.http import JsonResponse, QueryDict, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from online.order.models import Order, Order_Goods, OrderAddress
from online.goods.models import Goods
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
                return JsonResponse({"errcode": 19, "data": "用户不存在"})

            carts = Cart.objects.filter(user_id=user_id)
            for cart in carts:
                good_id = cart.goods_id
                quantity = cart.quantity
                try:
                    good_detail = Goods.objects.get(id=good_id)
                    good_name_en = good_detail.name_en
                    good_price = good_detail.price
                    good_description_en = good_detail.description_en
                    good_image = str(good_detail.image)
                    good_dict.append({"id": good_id, "quantity": quantity, "name_en": good_name_en, "price": good_price,
                                      "description_en": good_description_en, "image": good_image})
                    total = total + quantity * good_price

                except Exception as e:
                    online_logger.error(e)
                    return JsonResponse({"errcode": 10, "data": "数据库错误"})
            res = {"user_info": user_info, "good_dict": good_dict, "total": total}

            tpl = get_template("myOrder.html")
            res = tpl.render(res)
            return HttpResponse(res)

        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": 13, "data": "数据库错误"})


# 【渲染】订单详情
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
                return JsonResponse({"res": 111, "errmsg": "数据库错误"})
            if goods != '':
                good_dic = []
                for good in goods:
                    good_id = good.goods_id
                    quantity = good.quantity
                    good_detail = Goods.objects.get(id=good_id)
                    good_name_en = good_detail.name_en
                    good_price = good_detail.price
                    good_description_en = good_detail.description_en
                    good_image = str(good_detail.image)
                    good_dic.append({"quantity": quantity, "good_name_en": good_name_en, "good_price": good_price,
                                      "good_description_en": good_description_en, "good_image": good_image})
                res = {"good_dic": good_dic}
                tpl = get_template("orderDetail.html")
                data = tpl.render(res)
                return JsonResponse({'errcode': 4, 'data': data})
            else:
                return JsonResponse({'errcode': 5, 'data': "商品不存在"})
        else:
            return JsonResponse({'errcode': 4, 'data': "订单不存在"})


# 【渲染】订单列表
class OrdersListView(View):
    @method_decorator(user_auth)
    def get(self, request, user):
        user_id = user.id
        status_query = request.GET.get('status')
        order_no = request.GET.get('order_no')

        orders = Order.objects.filter(user_id=user_id).order_by('-order_date')
        if order_no:
            try:
                orders = orders.filter(order_no=order_no)
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({'errcode': 4, 'data': "数据格式错误"})
        else:
            if status_query:
                try:
                    status_query = int(status_query)
                except ValueError as e:
                    online_logger.error(e)
                    return JsonResponse({'errcode': 1, 'data': "状态码错误"})
                try:
                    orders = orders.filter(status=status_query).order_by('-order_date')
                except Exception as e:
                    online_logger.error(e)
                    return JsonResponse({'errcode': 4, 'data': "数据格式错误"})

        if orders.count() > 10:
            next_page = 1
            orders = orders[:10]
        else:
            next_page = 0

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
                return JsonResponse({"errcode": 111, "data": "数据库错误"})
            if goods != '':
                for good in goods:
                    good_id = good.goods_id
                    quantity = good.quantity

                    good_detail = Goods.objects.get(id=good_id)
                    good_name_en = good_detail.name_en
                    good_price = good_detail.price
                    good_description_en = good_detail.description_en
                    good_image = str(good_detail.image)
                    good_dic.append({"id": good_id, "quantity": quantity, "name_en": good_name_en, "price": good_price,
                                     "description_en": good_description_en, "image": good_image})
            else:
                return JsonResponse({'errcode': 112, 'data': "商品不存在"})

            res = {"order_dic": order_dic, "good_dic": good_dic, "status": status_query, "next_page": next_page}
        else:
            res = {"order_dic": '', "good_dic": '', "status": status_query, "next_page": next_page}
        return render(request, "myOrders.html", context=res)


# 创建订单
class OrderView(View):

    # 创建订单
    @method_decorator(transaction.atomic)
    @method_decorator(csrf_exempt)
    @method_decorator(user_auth)
    def post(self, request, user):
        if request.POST:
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
                return JsonResponse({"errcode": 10, "data": "订单信息不完整"})
            else:
                user_id = user.id
                if phone_number.isdigit() and total.isdigit():
                    time = timezone.localtime(timezone.now()).strftime("%Y-%m-%d")
                    order_no = random.randint(0, 9999999999)
                    status = 0

                    save_id = transaction.savepoint()
                    order_address = OrderAddress.objects.create(name=name, province=province, road=road,
                                                                city=city, district=district, postcode=postcode,
                                                                phone_number=phone_number)

                    order = Order.objects.create(order_no=order_no, total=total, order_date=time, status=status,
                                                 address=order_address, user=User.objects.get(id=user_id))

                    for good in goods:
                        goods_id = good['good_id']
                        good_count = good['good_count']
                        try:
                            Goodgoods = Goods.objects.select_for_update().get(id=goods_id)
                        except Goods.DoesNotExist as e:
                            transaction.savepoint_rollback(save_id)
                            online_logger.error(e)
                            return JsonResponse({'errcode': 2, 'data': '商品信息错误'})
                        except Exception as e:
                            online_logger.error(e)
                            return JsonResponse({'errcode': 2, 'data': '数据库错误'})
                        count = int(good_count)

                        if Goodgoods.stock < count:
                            transaction.savepoint_rollback(save_id)
                            return JsonResponse({'errcode': 4, 'data': '库存不足'})

                        Goodgoods.sale += count
                        Goodgoods.stock -= count
                        Goodgoods.save()

                        goods = Goods.objects.select_for_update().get(id=goods_id)
                        Order_Goods.objects.create(order=order, goods=goods, quantity=count)

                    return JsonResponse({"errcode": 5, "data": "订单创建成功"})
                else:
                    return JsonResponse({"errcode": 9, "data": "订单信息格式不正确"})


# 翻页
class OrdersOffsetView(View):
    @method_decorator(user_auth)
    def get(self, request, user):
        user_id = user.id
        offset = request.GET.get('offset')
        status_query = request.GET.get('status')

        if offset and status_query:
            try:
                offset = int(offset)
            except ValueError as e:
                online_logger.error(e)
                return JsonResponse({'errcode': 1, 'data': "跳过条数格式错误"})
            try:
                orders = Order.objects.filter(user_id=user_id)[offset:offset + 10].order_by('-order_date')
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({'errcode': 4, 'data': "数据格式错误"})
            try:
                status_query = int(status_query)
            except ValueError as e:
                online_logger.error(e)
                return JsonResponse({'errcode': 1, 'data': "状态码错误"})
            try:
                orders = orders.filter(status=status_query).order_by('-order_date')
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({'errcode': 4, 'data': "数据格式错误"})

            if orders.count() > 10:
                next_page = 1
                orders = orders[:10]
            else:
                pass
                next_page = 0
            if orders.count() > 0:
                order_dic = []

                for order in orders:
                    order_no = order.order_no
                    order_date = order.order_date
                    total = order.total
                    status = order.get_status_display()
                    order_dic.append({"order_no": order_no, "order_date": order_date, "total": total, "status": status})
                res_order = {"order_dic": order_dic}
            else:
                res_order = {"order_dic": ''}
            tpl = get_template("orderBlock.html")
            data = tpl.render(res_order)
            return JsonResponse({"errcode": 0, "data": data, "next_page": next_page})
        else:
            return JsonResponse({"errcode": 1, "data": "跳过条数不存在"})


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
                    return JsonResponse({"errcode": 111, "data": "请求数据不全或格式错误"})
                if status.isdigit() and order_no.isdigit():

                    try:
                        order = Order.objects.get(order_no=order_no)
                    except Order.DoesNotExist as e:
                        online_logger.error(e)
                        return JsonResponse({"errcode": 111, "data": "订单不存在"})
                    except Exception as e:
                        online_logger.error(e)
                        return JsonResponse({"errcode": 111, "data": "数据库错误"})

                    else:
                        if order.status == 2:
                            return JsonResponse({"errcode": 222, "errmsg": "订单已完成，不能修改状态"})
                        order = Order.objects.get(order_no=order_no)
                        order.status = status
                        order.save()
                        return JsonResponse({"errcode": 5, "data": "订单状态修改成功"})
                else:
                    return JsonResponse({"errcode": 8, "data": "订单状态或订单号不正确"})
            else:
                return JsonResponse({"errcode": 7, "data": "未收到请求内容或请求方式错误"})
        else:
            return JsonResponse({"errcode": 6, "data": "请求方式错误"})
