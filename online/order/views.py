from django.db import transaction
from django.shortcuts import render
from django.template.loader import get_template
from django.utils.decorators import method_decorator
from django.http import JsonResponse, QueryDict, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from online.constants import PER_PAGE_GOODS_COUNT
from online.order.models import Order, Order_Goods, OrderAddress
from online.goods.models import Goods, Image
from management.user.models import User
from online.logger import online_logger
from utils.decorator import user_auth
from online.cart.models import Cart
from management.user.models import UserAddress
import management.user

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
        if user_id:
            try:
                user = UserAddress.objects.get(user_id=user_id)
                name = user.name
                province = user.province
                city = user.city
                district = user.district
                road = user.road
                phone_number = user.phone_number
                postcode = user.postcode
                is_null = 0
            except management.user.models.UserAddress.DoesNotExist:
                name = ''
                province = ''
                city = ''
                district = ''
                road = ''
                phone_number = ''
                postcode = ''
                is_null = 1
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({"errcode": 4, "errmsg": "数据库错误"})

            orders = Order.objects.filter(user_id=user_id)
            order_quantity = len(orders)
            cart_quantity = request.session.get("%s_cart" % user_id, 0)
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

                    total = total + quantity * good_price
                    good_dict.append({"id": good_id, "quantity": quantity, "name_en": good_name_en, "price": good_price,
                                      "description_en": good_description_en, "image": good_image})
                except Exception as e:
                    online_logger.error(e)
                    return JsonResponse({"errcode": 10, "errmsg": "数据库错误"})

            user_info = {"name": name, "province": province, "city": city, "district": district,
                         "road": road, "phone_number": phone_number, "postcode": postcode, "is_null": is_null}
            res = {"user_info": user_info, "good_dict": good_dict, "total": total, "user": user,
                   "cart_quantity": cart_quantity, "order_quantity": order_quantity}
            tpl = get_template("myOrder.html")
            res = tpl.render(res)
            return HttpResponse(res)

        else:
            JsonResponse({"errcode": 6, "errmsg": "用户不存在"})


# 订单详情
class OrdersDetailView(View):
    @method_decorator(user_auth)
    def get(self, request, user):
        user_id = request.session.get("user_id", None)
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
                    good_name_en = good.name_en
                    good_price = good.on_price
                    good_description_en = good.description_en
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
        user_id = request.session.get("user_id", None)
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
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": 10, "errmsg": "订单信息不完整"})

        user_id = request.session.get("user_id", None)
        time = timezone.localtime(timezone.now()).strftime("%Y-%m-%d")
        order_no = random.randint(0, 9999999999)
        status = 0
        total = 0

        save_id = transaction.savepoint()
        try:
            order_address = OrderAddress.objects.create(name=name, province=province, road=road,
                                                        city=city, district=district, postcode=postcode,
                                                        phone_number=phone_number)

            order = Order.objects.create(order_no=order_no, total=total, order_date=time, status=status,
                                         address=order_address, user=User.objects.get(id=user_id))
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": 3, "errmsg": "数据格式错误"})

        for good in goods:
            goods_id = good['id']
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

            name_en = Goodgoods.name_en
            on_price = Goodgoods.on_price
            description_en = Goodgoods.description_en

            good_img = Image.objects.filter(goods_id=goods_id)[0].image

            Goodgoods.actual_sale += count
            Goodgoods.stock -= count
            Goodgoods.save()
            total += good_count * Goodgoods.on_price

            Order_Goods.objects.create(order=order, quantity=count, name_en=name_en, on_price=on_price,
                                       description_en=description_en, img=good_img)
            Order.objects.filter(id=order.id).update(total=total)

        href = "http://10.168.2.111:8000/orders/{order_id}/pay/".format(order_id=order.id)
        return JsonResponse({"errcode": 0, "data": {"result": "订单创建成功", "href": href}})


# 翻页
class OrdersOffsetView(View):
    @method_decorator(user_auth)
    def get(self, request, user):
        user_id = request.session.get("user_id", None)
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
            UserAddress.objects.get(user_id=user_id)
            UserAddress.objects.filter(user_id=user_id).update(name=name, province=province, road=road,
                                                               city=city, district=district, postcode=postcode,
                                                               phone_number=phone_number)
            return JsonResponse({"errcode": 0, "data": {"result": "地址修改成功"}})
        except management.user.models.UserAddress.DoesNotExist:
            try:
                UserAddress.objects.create(user_id=user_id, name=name, province=province, road=road,
                                           city=city, district=district, postcode=postcode, phone_number=phone_number)
                return JsonResponse({"errcode": 0, "data": {"result": "地址保存成功"}})
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({"errcode": 4, "errmsg": "数据库错误"})
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": 3, "errmsg": "数据格式错误"})


# 【渲染】订单页面（地址）
class OrderPayView(View):
    @method_decorator(user_auth)
    def get(self, request, user, order_id):
        res = {"abc": "abc"}
        tpl = get_template("payOrder.html")
        res = tpl.render(res)
        return HttpResponse(res)


# 订单支付
class PayOrder(View):
    @method_decorator(user_auth)
    def get(self, request, user, order_id):
        user = User.objects.filter(user.id)
        if user != '':
            try:
                order = Order.objects.update(status=1)
                order.save()
                index_href = "http://10.168.2.111:8000/index/"
                return JsonResponse({"errcode": 0, "errmsg": "订单支付成功", "href": index_href})
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({"errcode": 4, "errmsg": "数据库错误"})
