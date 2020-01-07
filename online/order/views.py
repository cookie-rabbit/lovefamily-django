from django.db import transaction
from django.shortcuts import render
from django.template.loader import get_template
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from paypal.standard.forms import PayPalPaymentsForm

from online.constants import PER_PAGE_GOODS_COUNT
from online.order.models import Order, Order_Goods, OrderAddress, OrderStatusLog
from online.goods.models import Goods, Image
from management.user.models import User
from online.logger import online_logger
from utils.decorator import user_auth
from online.cart.models import Cart
from management.user.models import UserAddress
import management.user

import ast
import random
from datetime import datetime

# 【渲染】订单页面（地址）
from weigan_shopping import settings


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
                return JsonResponse({"errcode": "102", "errmsg": "db error"})

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
                    good_image = Image.objects.filter(goods_id=good_id)

                    total = total + quantity * good_price
                    good_dict.append({"id": good_id, "quantity": quantity, "name_en": good_name_en, "price": good_price,
                                      "description_en": good_description_en,
                                      "image": settings.URL_PREFIX + good_image[0].image.url})
                except Exception as e:
                    online_logger.error(e)
                    return JsonResponse({"errcode": "102", "errmsg": "db error"})

            user_info = {"name": name, "province": province, "city": city, "district": district,
                         "road": road, "phone_number": phone_number, "postcode": postcode, "is_null": is_null}
            res = {"user_info": user_info, "good_dict": good_dict, "total": total, "user": user,
                   "cart_quantity": cart_quantity, "order_quantity": order_quantity}
            tpl = get_template("myOrder.html")
            res = tpl.render(res)
            return HttpResponse(res)

        else:
            JsonResponse({"errcode": 101, "errmsg": "user_id is None"})


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
                return JsonResponse({"errcode": 102, "errmsg": "db error"})
            if goods != '':
                good_dic = []
                for good in goods:
                    quantity = good.quantity
                    good_name_en = good.name_en
                    good_price = good.on_price
                    good_description_en = good.description_en
                    good_image = Image.objects.filter(goods_id=good.id)
                    good_dic.append({"quantity": quantity, "name_en": good_name_en, "price": good_price,
                                     "description_en": good_description_en,
                                     "image": settings.URL_PREFIX + good_image[0].image.url})
                res = {"good_dic": good_dic}
                tpl = get_template("orderDetail.html")
                data = tpl.render(res)
                return JsonResponse({'errcode': 0, 'data': data})
            else:
                return JsonResponse({"errcode": 110, "errmsg": "goods not exist"})
        else:
            return JsonResponse({'errcode': 111, 'errmsg': "order not exist"})


# 【渲染】订单列表
class OrdersListView(View):
    @method_decorator(user_auth)
    def get(self, request, user):
        user_id = request.session.get("user_id", None)
        status_query = request.GET.get('status', 0)

        orders = Order.objects.filter(user_id=user_id).order_by('-order_date')
        order_quantity = len(orders)
        try:
            status_query = int(status_query)
        except ValueError as e:
            online_logger.error(e)
            return JsonResponse({'errcode': 101, 'errmsg': "params error"})
        try:
            if status_query == 0:
                orders_total = orders.order_by('-order_date')
            else:
                orders_total = orders.filter(status=status_query).order_by('-order_date')
            orders = orders_total[: PER_PAGE_GOODS_COUNT]

        except Exception as e:
            online_logger.error(e)
            return JsonResponse({'errcode': 101, 'errmsg': "params error"})
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
                return JsonResponse({"errcode": 102, "errmsg": "db error"})
            if goods != '':
                for good in goods:
                    quantity = good.quantity

                    good_name_en = good.name_en
                    good_price = good.on_price
                    good_description_en = good.description_en
                    good_image = str(good.img)
                    good_dic.append({"quantity": quantity, "name_en": good_name_en, "price": good_price,
                                     "description_en": good_description_en, "image": good_image})
            else:
                return JsonResponse({'errcode': 110, 'errmsg': "goods not exist"})
        else:
            order_dic = []
            good_dic = []

        cart_quantity = request.session.get("%s_cart" % user_id)
        res = {"order_dic": order_dic, "good_dic": good_dic, "status": status_query, "more": more,
               "cart_quantity": cart_quantity, "order_quantity": order_quantity}
        return render(request, "myOrders.html", context=res)


class OrderCreateView(View):
    # 创建订单
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
            return JsonResponse({"errcode": 101, "errmsg": "params not all"})

        user_id = request.session.get("user_id", None)
        time = timezone.localtime(timezone.now()).strftime("%Y-%m-%d")

        i = datetime.now()
        order_no = "0000" + str(i.year) + str(i.month) + str(i.day) + str(i.hour) + str(i.minute) + str(
            i.second) + str(random.randint(0000, 9999))
        status = 1
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
            return JsonResponse({"errcode": 101, "errmsg": "params error"})

        for good in goods:
            goods_id = good['good_id']
            good_count = good['good_count']
            try:
                Goodgoods = Goods.objects.select_for_update().get(id=goods_id)
            except Goods.DoesNotExist as e:
                transaction.savepoint_rollback(save_id)
                online_logger.error(e)
                return JsonResponse({'errcode': 110, 'errmsg': "goods not exist"})
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({'errcode': 102, 'errmsg': 'db error'})
            count = int(good_count)

            if Goodgoods.stock < count:
                transaction.savepoint_rollback(save_id)
                return JsonResponse({'errcode': 112, 'errmsg': "stock not enough"})

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

        time = timezone.localtime(timezone.now()).strftime("%Y-%m-%d %H:%M:%S")
        OrderStatusLog.objects.create(order_no=order_no, status=1, user_id=user_id, change_date=time)

        href = "http://10.168.2.111:8000/orders/{order_id}/pay/".format(order_id=order.id)
        return JsonResponse({"errcode": 0, "data": {"result": "ordered success", "href": href}})

    # 翻页
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
            return JsonResponse({'errcode': 101, 'errmsg': "params error"})
        try:
            if status_query == 0:
                orders_total = Order.objects.filter(user_id=user_id).order_by('-order_date')
            else:
                orders_total = Order.objects.filter(user_id=user_id, status=status_query).order_by('-order_date')
            orders = orders_total[offset:offset + PER_PAGE_GOODS_COUNT]
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({'errcode': 102, 'errmsg': "db error"})

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
            return JsonResponse({"errcode": 101, "errmsg": "params not all"})
        try:
            UserAddress.objects.filter(user_id=user_id).update(name=name, province=province, road=road,
                                                               city=city, district=district, postcode=postcode,
                                                               phone_number=phone_number)
            return JsonResponse({"errcode": 0, "errmsg": "updated success"})
        except management.user.models.UserAddress.DoesNotExist:
            try:
                UserAddress.objects.create(user_id=user_id, name=name, province=province, road=road,
                                           city=city, district=district, postcode=postcode, phone_number=phone_number)
                return JsonResponse({"errcode": 0, "data": "created success"})
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({"errcode": 102, "errmsg": "db error"})
        except Exception as e:
            online_logger.error(e)
            return JsonResponse({"errcode": 102, "errmsg": "db error"})


# 【渲染】订单页面（地址）
class OrderPayView(View):
    @method_decorator(user_auth)
    def get(self, request, user, order_id):
        paypal_dict = {
            "business": "sb-cfr9k847350@business.example.com",
            "amount": "10000000.00",
            "item_name": "name of the item",
            "invoice": "unique-invoice-id",
            "notify_url": "www.baidu.com",
            "return": "www.baidu.com",
            "cancel_return": "www.baidu.com",
            "custom": "premium_plan",  # Custom command to correlate to some function later (optional)
        }

        form = PayPalPaymentsForm(initial=paypal_dict)
        context = {"form": form}
        return render(request, "payOrder.html", context)


# 订单支付
class PayOrder(View):
    @method_decorator(user_auth)
    def get(self, request, user, order_id):
        user = User.objects.filter(user.id)
        if user != '':
            try:
                order = Order.objects.filter(id=order_id).update(status=1)
                order.save()
                index_href = "http://10.168.2.111:8000/index/"
                return JsonResponse({"errcode": 0, "errmsg": "pay success", "href": index_href})
            except Exception as e:
                online_logger.error(e)
                return JsonResponse({"errcode": 102, "errmsg": "db error"})
